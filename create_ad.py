import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.admin._trafficguard.decorators import json_form_request
from apps.sponsored_links.utils import create_ad_container, create_ads, create_zone
from apps.sponsored_links.forms.create_ad_request import CreateAdRequest
from apps.sponsored_links_reporting.models import AdContainer, KeywordNew, Template, TrafficGuardCampaign

LOGGER = logging.getLogger(__name__)


@method_decorator(json_form_request(CreateAdRequest), name="dispatch")
class CreateAd(LoginRequiredMixin, View):
    """
    Creates an ad.

    Return:
        JsonResponse: success or error message.
    """
    def post(self, request, form_payload) -> JsonResponse:
        try:
            data = json.loads(request.body.decode("utf-8"))
            zone_details = data["zoneDetails"]
            campaign_id = data["campaignId"]
            keywords = data["keywords"][0].split('\n')
            ad_iterations = data["ad_iterations"]
            template_id = int(data["template_id"])

            campaign = TrafficGuardCampaign.objects.get(id=campaign_id)

            try:

                # Create the zone
                zone = create_zone(
                    zone_details["name"],
                    zone_details["width"],
                    zone_details["height"],
                    zone_details["site"]
                )

            except Exception as ex:
                print("Error creating zone: ", ex)
                return JsonResponse({"status": "error", "message": str(ex)})

            try:
                # Retrieve keyword_ids list
                keyword_ids = []
                for kw in keywords:
                    try:
                        keyword_obj = KeywordNew.objects.get(keyword=kw)
                        keyword_ids.append(keyword_obj.id)
                    except KeywordNew.DoesNotExist:

                        print(f"Keyword '{kw}' does not exist.")

            except Exception as ex:
                print("Error retrieving keyword ids: ", ex)
                return JsonResponse({"status": "error", "message": str(ex)})

            try:

                # Use the existing function to create the AdContainer
                ad_container = create_ad_container(
                    name=data["name"],
                    title="Sponsored Links",
                    zone_id=zone.id,
                    template_id=template_id,
                    keyword_ids=keyword_ids,
                    campaign_id=campaign_id
                )

            except Exception as ex:
                print("Error creating ad container: ", ex)
                return JsonResponse({"status": "error", "message": str(ex)})

            try:
                print("ad container: ", ad_container)
                print("ad iterations: ", ad_iterations)
                print("campaign: ", campaign)
                # Now handle the creation of ads
                create_ads(ad_container, ad_iterations, campaign)

            except Exception as ex:
                print("Error creating Ads: ", ex)
                return JsonResponse({"status": "error", "message": str(ex)})


            return JsonResponse({"status": "success", "message": "Ad container and ads created successfully."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
