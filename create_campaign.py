from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.sponsored_links.serializers import NewCampaign
from apps.operations.models import Registrar
from apps.main_app.providers import trafficguard
from apps.data.trafficguard.models import Categories, RoutingDomains, Campaigns
from apps.operations.models import RegisteredDomains
import base64
import random
from datetime import datetime
from django.contrib.auth.models import User
from apps.data.models import UserProfile
from apps.admin._trafficguard.campaign_wizard.utils import buy_domain
from apps.sponsored_links.create_crux_campaign import CreateCruxCampaign
from apps.sponsored_links_reporting.models import Category

class CreateCampaign(LoginRequiredMixin, APIView):

    serializer_class = NewCampaign

    def post(self, request, user_id):
        """
        Creates a standalone Sponsored Links campaign.
        """

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            publisher = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(owner_id=user_id)
            data = serializer.data
            category = Categories.objects.get(id=data.get("category_id"))
            routing_domain = RoutingDomains.objects.get(id=data.get("routing_domain_id"))

            raw_campaign = {
                "name": data.get("name"),
                "crossroads_user_id": user_id,
                "status": "active",
                "type": Campaigns.TYPE_SPONSORED_LINKS_TYPE,
                "start_date": datetime.today().strftime("%Y-%m-%d"),
                "category_ids": [data.get("category_id")],
                "no_cloaking": True,
                "routing_domain": {
                    "default_domain": routing_domain.default_domain,
                    "name": routing_domain.name,
                    "is_https": True,
                    "status": "active",
                },
                "redirection_rules": [],
            }

            for rule in data.get("redirection_rules"):
                kw_list_ids = rule.get("keyword_list_ids", [])
                raw_campaign["redirection_rules"].append(
                    {
                        "status": "active",
                        "device_type": "",
                        "country_codes": "",
                        "status": "active",
                        "use_keyword_list": True,
                        "passthrough_parameters": ["sl_kw"],
                        "device_type_ids": ["1", "2", "3"],
                        "keyword_list_ids": kw_list_ids,
                        "keyword_lists": (
                            [
                                {
                                    "id": kw_list_id,
                                    "percentage": (
                                        (1 / len(kw_list_ids)) * 100
                                    ),
                                }
                                for kw_list_id in kw_list_ids
                            ]
                            if len(kw_list_ids)
                            else []
                        ),
                        "revenue_domains": [
                            {
                                "name": domain["name"],
                                "percentage": 100,
                                "revenue_provider_id": domain["revenue_provider_id"],
                                "status": "active",
                                "is_https": True,
                            }
                            for domain in rule["revenue_domains"]
                        ],
                        "safe_domain": {
                            "name": rule.get("safe_domain", {}).get(
                                "name", "primeinfospot.com"
                            ),
                            "status": "active",
                        },
                    }
                )

            response = trafficguard.create_campaign(raw_campaign).json()

            # buy domain
            if response['valid']:

                for rule in data.get("redirection_rules", []):
                    for revenue_domain in rule["revenue_domains"]:
                        if not RegisteredDomains.objects.filter(domain=data.get("domain")).exists():
                            buy_domain(
                                registrar_id=Registrar.objects.get(
                                    user_name="aerobuster"
                                ).id,
                                domain_name=revenue_domain.get("name"),
                                notify_user_id=publisher.id,
                                user_id=publisher.id,
                                category_name=category.name,
                                tpa_id=data.get("tpa_id"),
                                rev_provider_id=profile.default_revenue_provider_id,
                                tg_ssl=data.get("https_enabled", False),
                                random_digit=str(
                                    random.randrange(100000, 100000000000000)
                                ),
                                use_domain_parking=(
                                    True
                                    if int(data.get("use_domain_parking", False)) != 0
                                    else False
                                ),
                                use_imprinting=(
                                    True
                                    if int(data.get("use_imprinting", False)) != 0
                                    else False
                                ),
                                # check serializer for validation options
                                serp_pixel=(
                                    base64.b64decode(data.get("serp_pixel", "")).decode(
                                        "utf-8"
                                    )
                                    if profile.use_pixels
                                    else None
                                ),
                                lander_pixel=(
                                    base64.b64decode(
                                        data.get("lander_pixel", "")
                                    ).decode("utf-8")
                                    if profile.use_pixels
                                    else None
                                ),
                                adclick_pixel=(
                                    base64.b64decode(
                                        data.get("adclick_pixel", "")
                                    ).decode("utf-8")
                                    if profile.use_pixels
                                    else None
                                ),
                                html_header=data.get("html_header", ""),
                            )

                CreateCruxCampaign.create_tg_campaign(
                    data.get("name"),
                    response["campaign"],
                    Category.objects.get(id=data.get("sponsored_links_category_id")),
                )

                return JsonResponse(response["campaign"], status=201)

        return JsonResponse(serializer.errors, status=422, safe=False)
