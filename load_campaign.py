from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from apps.sponsored_links_reporting.models import TrafficGuardCampaign, Ad
from apps.main_app.providers.trafficguard import get_campaign

class LoadCampaign(LoginRequiredMixin, View):
    """
    Loads a list of publisher sponsored links campaigns.

    Args:
        campaign_id(int): Campaign ID

    Return:
        JsonResponse: List of campaigns.
    """

    def get(self, request, campaign_id: int) -> JsonResponse:

        tg_campaign = get_campaign(campaign_id).json().get("campaign")

        sponsored_links_campaign = TrafficGuardCampaign.objects.get(id=campaign_id)

        ads = list(
            Ad.objects.filter(
                adlink__campaign_keyword__tg_campaign_id=campaign_id,
                adlink__rev_url__isnull=True,
            )
            .distinct("container__id")
            .values(
                "container__name",
                "container__id",
                "container__zone_id",
                "container__zone__name",
                "container__zone__site_id",
            )
        )

        return JsonResponse(
            {
                "tg_campaign": tg_campaign,
                "sponsored_links_campaign": {"name": sponsored_links_campaign.name},
                "ads": ads,
            },
            safe=False,
        )
