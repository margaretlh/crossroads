"""
Views for managing White Label configurations, publishers, and reports.

This module contains Django class-based views that handle various
White Label-related functionalities, including:
- Managing White Label configurations
- Associating publishers and admins
- Handling revenue-sharing rules
- Generating reports
"""

import json
import re
from datetime import datetime

import pandas as pd
from django_tables2 import RequestConfig

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from apps.accounting.models import LineItem
from apps.accounting.views import ApiView
from apps.admin._trafficguard.decorators import has_permissions, json_form_request
from apps.data.models import CrossroadPermission, RevenueCalcType
from apps.dwh.tasks import deactivate_whitelabel_configuration
from apps.main_app.helpers import DownloadCsv, df_to_list_dict, get_summary_table_dates
from apps.whitelabel.form_requests.add_admin import AddAdmin
from apps.whitelabel.form_requests.associate_publisher import AssociatePublisher
from apps.whitelabel.form_requests.updated_white_label_settings import (
    UpdatedWhiteLabelSettings,
)
from apps.whitelabel.forms import (
    AssociatePublisherForm,
    NewWhiteLabelConfiguration,
    WlConfigForm,
    WlPublisherSettingsForm,
    WlRuleForm,
)
from apps.whitelabel.models import WhiteLabelConfiguration, WLPublisher, WLShareRule
from apps.whitelabel.tables import (
    WhiteLabelIndexTable,
    WlPublisherReportTable,
    WlShareRuleTable,
)
from apps.whitelabel.wl_reports import WlReportManager


class WhiteLabelIndex(LoginRequiredMixin, View):
    """
    - View for displaying the White Label configurations index page
    - Allows users to create new white Label configuration and filter by config status (active/inactive/all).
    """

    def get(self: "WhiteLabelIndex", request:HttpRequest) -> HttpResponse:
        """Handles GET requests and returns an HTML response with White Label configurations."""
        status_filter = request.GET.get("status", "all")

        if request.user.has_perm("data.admin"):
            if status_filter == "inactive":
                wl_instances = WhiteLabelConfiguration.objects.filter(active=False).values("id", "name", "active")
            elif status_filter == "active":
                wl_instances = WhiteLabelConfiguration.objects.filter(active=True).values("id", "name", "active")
            else:
                wl_instances = WhiteLabelConfiguration.objects.all().values("id", "name", "active")
        elif status_filter == "inactive":
            wl_instances = WhiteLabelConfiguration.objects.filter(
                admins=request.user, active=False
            ).values("id", "name", "active")
        elif status_filter == "active":
            wl_instances = WhiteLabelConfiguration.objects.filter(
                admin=request.user, active=True
            ).values("id", "name", "active")
        else: # Show all White Label Configurations
            wl_instances = WhiteLabelConfiguration.objects.filter(
                admins=request.user
            ).values("id", "name", "active")

        table = WhiteLabelIndexTable(wl_instances)
        RequestConfig(request).configure(table)
        return render(
            request,
            "whitelabel/wl_configs.html",
            {
                "table": table,
                "config_form": NewWhiteLabelConfiguration(
                    {"action": "/whitelabel/store/"}
                ),
                "status_filter": status_filter,
            },
        )

class WhiteLabelSettings(LoginRequiredMixin, View):
    """This class handles the White Label configuration settings for authenticated users."""

    def get(self: "WhiteLabelSettings", request: HttpRequest, wl_id: int) -> HttpResponse:
        """Handles GET requests to fetch White Label settings."""
        is_super_admin = "true" if request.user.has_perm("data.super_admin") else "false"

        context = {
            "white_label_id": wl_id,
            "is_super_admin": is_super_admin
        }
        return render(request, "whitelabel/wl_settings.html", context)

    def post(self: "WhiteLabelSettings", request: HttpRequest, wl_id: int) -> HttpResponse:
        """Handles POST requests to update White Label settings."""
        try:
            config = WhiteLabelConfiguration.objects.get(id=wl_id)
        except WhiteLabelConfiguration.DoesNotExist:
            return HttpResponse("Configuration not found")
        action = request.POST.get("action", "none")

        if not (
            config.is_wl_admin(request.user) or request.user.has_perm("data.admin")
        ):
            return HttpResponse("No permission to access page!")

        if action == "associate_user":
            form = AssociatePublisherForm(request.POST)
            if form.is_valid():
                WLPublisher.objects.get_or_create(
                    configuration_id=wl_id, publisher_id=form.data.get("user")
                )
        elif action == "associate_admin":
            form = AssociatePublisherForm(request.POST)
            if form.is_valid():
                u = User.objects.get(id=form.data.get("user"))
                config.admins.add(u)
                if not u.has_perm("data.whitelabel_admin"):
                    u.user_permissions.add(
                        CrossroadPermission.objects.get_permission(
                            codename="whitelabel_admin"
                        )
                    )
        elif action == "save_settings":
            form = WlConfigForm(request.POST)
            if form.is_valid():
                config.name = form.data.get("name")
                config.title = form.data.get("title")
                config.pay_difference_to_id = form.data.get("pay_difference_to_id")
                config.logo_icon = form.data.get("logo_icon")
                config.primary_color = form.data.get("primary_color")
                config.secondary_color = form.data.get("secondary_color")
                config.text_color = form.data.get("text_color")
                config.save()
        return redirect(f"/whitelabel/{wl_id}")


class WhiteLabelPubDetail(LoginRequiredMixin, View):
    """This class handles the White Label Publisher details for authenticated users."""
    def get(self: "WhiteLabelPubDetail", request: HttpRequest, wl_pub_id: int) -> HttpResponse:
        """Handles GET requests to fetch White Label Publisher details."""
        wl_pub = WLPublisher.objects.get(id=wl_pub_id)
        if not (
                wl_pub.configuration.is_wl_admin(request.user)
                or request.user.has_perm("data.admin")
        ):
            return HttpResponse("No permission to access page!")

        rules = WLShareRule.objects.filter(owner=wl_pub.publisher)
        table = WlShareRuleTable(rules)
        RequestConfig(request).configure(table)

        wl_pub_settings = [("Bucket", wl_pub.get_bucket_display())]

        context = {
            "rule_table": table,
            "add_rule_form": WlRuleForm,
            "publisher_settings_form": WlPublisherSettingsForm(
                initial={"bucket": wl_pub.bucket}
            ),
            "configuration": wl_pub.configuration,
            "publisher_name": wl_pub.publisher.username,
            "wl_publisher_id": wl_pub.id,
            "wl_pub_settings": wl_pub_settings,
        }

        return render(request, "whitelabel/wl_pub_detail.html", context)

    def post(self: "WhiteLabelPubDetail", request: HttpRequest, wl_pub_id: int) -> HttpResponse:
        """Handles POST requests to update Publisher details under White Label Config."""
        action = request.POST.get("action")
        wl_pub = WLPublisher.objects.get(id=wl_pub_id)
        if not (
            wl_pub.configuration.is_wl_admin(request.user)
            or request.user.has_perm("data.admin")
        ):
            return HttpResponse("No permission to access page!")
        if action == "add_rule":
            form = WlRuleForm(request.POST)
            if form.is_valid():
                w, _ = WLShareRule.objects.update_or_create(
                    owner=wl_pub.publisher,
                    date_effective=form.data.get("date_effective"),
                    defaults={
                        "percentage": float(form.data.get("percentage")) / 100,
                    },
                )
        elif action == "update_publisher":
            bucket_type = request.POST.get("bucket")
            wl_pub.bucket = bucket_type
            wl_pub.save()
        return redirect(f"/whitelabel/detail/{wl_pub_id}")


@method_decorator(json_form_request(AssociatePublisher), name="dispatch")
class AssociatePublisherWithWhiteLabel(ApiView):
    """This class handles associating a Publisher with a White Label configuration."""
    def post(
            self: "AssociatePublisherWithWhiteLabel",
            request: HttpRequest,
            white_label_id: int,
            form_payload: dict
    ) -> JsonResponse:
        """Handles POST requests to associate a Publisher with a White Label configuration."""
        WLPublisher.objects.get_or_create(
            configuration_id=white_label_id,
            publisher_id=form_payload.get("publisher_id"),
        )
        return JsonResponse({
            "message": "Publisher associated with White Label.",
            "request_method": request.method,
        })


@method_decorator(has_permissions(["data.admin"]), name="dispatch")
class RemovePubFromConfiguration(LoginRequiredMixin, View):
    """This class handles removing a Publisher from a White Label configuration."""
    def get(self: "RemovePubFromConfiguration", request: HttpRequest, wl_pub_id: int) -> HttpResponse:
        """Handles GET requests to remove a Publisher from a White Label configuration."""
        action = request.GET.get(
            "action", "set_to_100"
        )  # 'set_to_100' or 'remove_rules'
        wl_pub = WLPublisher.objects.get(id=wl_pub_id)
        if not (
            wl_pub.configuration.is_wl_admin(request.user)
            or request.user.has_perm("data.admin")
        ):
            return HttpResponse("No permission to access page!")
        user_id = wl_pub.publisher_id
        config_id = wl_pub.configuration_id
        wl_pub.delete()
        if action == "set_to_100":
            WLShareRule.objects.update_or_create(
                owner_id=user_id,
                date_effective=datetime.now(tz=timezone.utc).date(),
                defaults={"percentage": 1.0},
            )
        return redirect(f"/whitelabel/{config_id}")


class WhiteLabelPubReport(LoginRequiredMixin, View):
    """This class handles exporting White Label Publisher Reports.
    request: The HTTP request object.
    wl_id: The white label configuration ID.
    """
    def get(self: "WhiteLabelPubReport", request: HttpRequest, wl_id: int) -> HttpResponse:
        """Handles GET requests to get White Label Publisher Report."""
        start_date, end_date = get_summary_table_dates(request)
        try:
            config = WhiteLabelConfiguration.objects.get(id=wl_id)
        except WhiteLabelConfiguration.DoesNotExist:
            return HttpResponse("Configuration not found")
        if not (
            config.is_wl_admin(request.user) or request.user.has_perm("data.admin")
        ):
            return HttpResponse("No permission to access page!")
        report_manager = WlReportManager(config, start_date, end_date)
        try:
            data = report_manager.get_reports()
        except ValueError as e:
            data = report_manager.empty_df()
            return e

        if request.GET.get("export", "false").lower() == "true":
            with pd.option_context("display.float_format", "${:,.2f}".format):
                data = data[
                    [
                        "username",
                        "bucket",
                        "total_visitors__sum",
                        "tracked_visitors__sum",
                        "owner_rev",
                        "pub_client_rev",
                        "diff",
                    ]
                ]
                data.rename(
                    columns={
                        "username": "Username",
                        "total_visitors__sum": "Gross Visitors",
                        "tracked_visitors__sum": "Tracked Visitors",
                        "owner_rev": "Partner Revenue",
                        "pub_client_rev": "Publisher Revenue",
                        "diff": "Partner Profit",
                    },
                )
                return DownloadCsv(
                    data_frame=data,
                    file_name=f"wl_publisher_report_{start_date}-{end_date}",
                ).download()

        table = WlPublisherReportTable(df_to_list_dict(data))
        RequestConfig(request, paginate={"per_page": 99999}).configure(table)

        context = {
            "table": table,
            "start_date": start_date,
            "end_date": end_date,
            "configuration": config,
        }
        return render(request, "whitelabel/wl_report.html", context)


class StoreWhiteLabelConfiguration(LoginRequiredMixin, View):
    """Handles the configuration for white-label stores."""
    def post(self: "StoreWhiteLabelConfiguration", request: HttpRequest) -> HttpResponse:
        """Handles POST request for configurating white-label stores."""
        form = NewWhiteLabelConfiguration(request.POST)
        if not form.is_valid():
            return HttpResponse("Please review your input")

        config_name = form.data.get("name")
        if not re.match("[a-zA-Z_$][0-9a-zA-Z_$]*", config_name):
            messages.add_message(request, messages.ERROR, "Wrong config name")
        else:
            config = WhiteLabelConfiguration()
            config.name = form.data.get("name")
            config.title = "Crossroads"
            config.pay_difference_to_id = form.data.get("pay_difference_to_id")
            config.logo_icon = "fa fa-search"
            config.primary_color = "#3663b5"
            config.secondary_color = "#eee"
            config.text_color = "#999"
            config.save()

        return redirect("/whitelabel/")


class LoadWhiteLabelSettings(ApiView):
    """This class handles loading White Label settings."""
    def get(self: "LoadWhiteLabelSettings", request: HttpRequest, white_label_id: int) -> JsonResponse:
        """Handles GET requests to load White Label settings."""
        try:
            config = WhiteLabelConfiguration.objects.get(id=white_label_id)
        except WhiteLabelConfiguration.DoesNotExist:
            return JsonResponse({"errors": "Configuration not found"}, status=401)
        if not (
            config.is_wl_admin(request.user) or request.user.has_perm("data.admin")
        ):
            return JsonResponse({"errors": "No permission to access page!"}, status=401)

        publishers = [
            {
                "publisher_id": wl_publisher.publisher.id,
                "publisher__username": wl_publisher.publisher.username,
                "id": wl_publisher.id,
                "bucket": wl_publisher.get_bucket_display(),
            }
            for wl_publisher in WLPublisher.objects.filter(configuration=config)
        ]

        return JsonResponse(
            {
                "publishers": publishers,
                "admins": list(config.admins.values("username")),
                "publisher_list": list(
                    User.objects.filter(is_active=True)
                    .order_by("username")
                    .distinct()
                    .values("id", "username")
                ),
                "config": {
                    "name": config.name,
                    "logo_icon": config.logo_icon,
                    "primary_color": config.primary_color,
                    "secondary_color": config.secondary_color,
                    "text_color": config.text_color,
                    "pay_difference_to_id": config.pay_difference_to_id,
                    "title": config.title,
                },
            }
        )


@method_decorator(json_form_request(UpdatedWhiteLabelSettings), name="dispatch")
@method_decorator(has_permissions(["data.admin"]), name="dispatch")
class UpdateWhiteLabelSettings(ApiView):
    """This class handles updating White Label Settings."""
    def post(
            self: "UpdateWhiteLabelSettings",
            request: HttpRequest,
            white_label_id:int,
            form_payload: dict
    ) -> JsonResponse:
        """Handles POST call to update White Label Settings."""
        user = request.user
        config = WhiteLabelConfiguration.objects.get(id=white_label_id)
        current_pay_difference_to_id = config.pay_difference_to_id
        config.name = form_payload.get("name")
        config.title = form_payload.get("title")
        config.pay_difference_to_id = form_payload.get("pay_difference_to_id")
        config.logo_icon = form_payload.get("logo_icon")
        config.primary_color = form_payload.get("primary_color")
        config.secondary_color = form_payload.get("secondary_color")
        config.text_color = form_payload.get("text_color")
        config.deactivation_date = form_payload.get("deactivation_date")
        config = WhiteLabelConfiguration.objects.get(id=white_label_id)
        config.save()

        if len(form_payload.get("effective_date", "")) > 0:
            line_items = LineItem.objects.filter(
                user_period__user_id=current_pay_difference_to_id,
                user_period__payment_period__start_date__gte=form_payload.get(
                    "effective_date"
                ),
            )

            for line_item in line_items:
                user_period = line_item.user_period.payment_period.get_user_period(
                    User.objects.get(id=form_payload.get("pay_difference_to_id")),
                    RevenueCalcType.objects.get_type(
                        form_payload.get("pay_difference_to_id")
                    ),
                )
                line_item.user_period_id = user_period.id
                line_item.save()

        return JsonResponse({
            "success": True,
            "message": "White Label Settings updated successfully",
            "updated_by": user.username
        })

@method_decorator(has_permissions(["data.super_admin"]), name="dispatch")
class DeactivateWhiteLabelSettings(ApiView):
    """This class handles the White Label Configuration Deactivation process."""
    def post(self: "DeactivateWhiteLabelSettings", request: HttpRequest, white_label_id: int) -> JsonResponse:
        """Handles POST calls to deactivate publisher's White Label settings."""
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            deactivation_date = data.get("deactivation_date", None)

            # If a deactivation date is selected
            if deactivation_date:
                # Fetch the white label configuration
                config = WhiteLabelConfiguration.objects.get(id=white_label_id)

                # Convert to date object
                deactivation_date_obj = datetime.strptime(deactivation_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                deactivation_date_obj = deactivation_date_obj.date()

                # Get today's date (date object)
                today = timezone.localdate()

                # Check if the deactivation date is in the past
                if deactivation_date_obj < today:
                    return JsonResponse({"errors": "Deactivation date cannot be in the past!"}, status=400)

                # If the selected date is today, run the deactivation immediately
                if deactivation_date_obj == today:
                    # Trigger the deactivation process right away
                    self._deactivate_white_label(config)
                    return JsonResponse({"message": "White Label Configuration has been deactivated today."})

                # Otherwise, schedule the deactivation for the future selected date and update the database
                # Convert the date object to a datetime object with a default time (e.g., midnight)
                deactivation_datetime_obj = datetime.combine(deactivation_date_obj, datetime.min.time())

                # config.deactivation_date type needs to store a date object type
                config.deactivation_date = deactivation_datetime_obj
                config.save()

                # Schedule the Celery task for the future deactivation date
                deactivate_whitelabel_configuration.apply_async(
                    eta=deactivation_datetime_obj
                )

                return JsonResponse(
                    {"message": f"White Label Configuration scheduled for deactivation on {deactivation_date}."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except WhiteLabelConfiguration.DoesNotExist:
            return JsonResponse({"error": "WhiteLabel configuration not found"}, status=404)

    def _deactivate_white_label(self: "DeactivateWhiteLabelSettings", config: WhiteLabelConfiguration) -> None:
        """Helper method to deactivate the white label configuration."""
        # Get all publishers associated with this White Label Configuration
        publishers = WLPublisher.objects.filter(configuration=config).values_list("publisher", flat=True)

        # Reset revenue share
        WLShareRule.objects.filter(owner_id__in=publishers).update(percentage=1.0)

        # Deactivate configuration and update the database
        config.active = False
        config.save()

@method_decorator(json_form_request(AddAdmin), name="dispatch")
@method_decorator(has_permissions(["data.admin"]), name="dispatch")
class AddAdminToWhiteLabel(ApiView):
    """This class handles adding assigning users as Admins to a White Label Configuration."""
    def post(
            self: "AddAdminToWhiteLabel",
            request: HttpRequest,
            white_label_id: int,
            form_payload:dict
    ) -> JsonResponse:
        """Handles POST call to link admins to White Label summary."""
        config = WhiteLabelConfiguration.objects.get(id=white_label_id)
        current_user = request.user

        user = User.objects.get(id=form_payload.get("admin_id"))
        config.admins.add(user)

        # Grant White Label permissions to each newly added Admin
        if config.active and not user.has_perm("data.whitelabel_admin"):
            user.user_permissions.add(
                CrossroadPermission.objects.get_permission(codename="whitelabel_admin")
            )

        return JsonResponse({
            "message": (
                f"User {user} added as admin to White Label {white_label_id} "
                f"by {current_user}"
            )
        })


@method_decorator(has_permissions(["data.admin"]), name="dispatch")
class RemoveAdminsFromWhiteLabel(ApiView):
    """This class handles removing Administrators from WhiteLabel view."""
    def post(self: "RemoveAdminsFromWhiteLabel", request: HttpRequest, white_label_id: int) -> JsonResponse:
        """Handles POST calls to remove admins from White Label Configurations."""
        user = request.user
        config = WhiteLabelConfiguration.objects.get(id=white_label_id)

        # Get all users associated with this WhiteLabel Configuration
        users = config.admins.all()

        permission = CrossroadPermission.objects.get_permission(codename="whitelabel_admin")

        # Revoke the 'whitelabel_admin' permission from all users associated with this WhiteLabel Configuration
        for user in users:
            if user.has_perm("data.whitelabel_admin"):
                user.user_permissions.remove(permission)
        return JsonResponse({"success": f"All users have been removed from whitelabel_admin permissions by {user}"})
