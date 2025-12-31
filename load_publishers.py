from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib.auth.models import User
from apps.data.models import UserAccess
import pandas
from apps.sponsored_links_reporting.models import TrafficGuardCampaign
from apps.sponsored_links_reporting.models import Site
from django.db.models import Count
from apps.main_app.helpers import df_to_list_dict

class LoadPublishers(LoginRequiredMixin, View):
    """
    Loads a list of publishers that have sponsored links campaigns.

    Return:
        JsonResponse: List of publishers.
    """

    def get(self, request) -> JsonResponse:

        filters = dict(
            user_permissions__codename__contains='publisher',
            is_active=True,
        )

        users = []

        # admin profile filters go here - account manager restrictions
        publisher_ids = UserAccess.objects.filter(owner=request.user).values_list('publisher_id', flat=True)
        if publisher_ids and not request.user.has_perm('data.super_admin'):
            filters['id__in'] = publisher_ids

        # Todo: Add a permission that prevents them even getting here
        # is_admin = request.user.has_perm("data.admin") or request.user.has_perm(
        #     "data.media_buyer"
        # )
        # if (not is_admin and len(publisher_ids) == 0) and not request.user.has_perm('data.manage_sponsored_links_categories'):
        #     return HttpResponse('not allowed!')

        if not request.user.has_perm('data.admin') and request.user.has_perm('data.media_buyer'):
            if 'id__in' in filters:
                del filters['id__in']
            filters['id'] = request.user.id

        if (
            request.user.has_perm('data.manage_sponsored_links_categories')
            and not request.user.has_perm('data.admin')
            and not request.user.has_perm('data.media_buyer')
        ):
            filters = {
                'id': request.user.id
            }

        users = pandas.DataFrame(
            data=list(
                User.objects.filter(**filters)
                .order_by("username")
                .values("id", "username")
                .distinct()
            ),
            columns=["id", "username"]
        )

        campaigns = pandas.DataFrame(
            data=list(
                TrafficGuardCampaign.objects.filter(
                    is_deleted=False,
                    version=TrafficGuardCampaign.VERSION_1,
                )
                .values("user_id")
                .annotate(campaign_count=Count("id"))
            ),
            columns=["user_id", "campaign_count"]
        )

        campaigns.rename(columns={"user_id": "id", "campaign_count": "campaigns"}, inplace=True)

        sites = pandas.DataFrame(
            data=list(
                Site.objects.filter(deleted=False)
                .exclude(user_id=None)
                .values("user_id")
                .annotate(site_count=Count("id"))
            ),
            columns=["user_id", "site_count"],
        )

        sites.rename(columns={"user_id": "id", "site_count": "sites"}, inplace=True)

        results = pandas.merge(users, sites, on="id", how="left").fillna('0')
        results = (
            pandas.merge(results, campaigns, on="id", how="left")
            .fillna(0)
            .reset_index()
        )
        results = results[results['campaigns'] > 0]

        return JsonResponse(
            df_to_list_dict(results),
            safe=False,
        )
