from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdContainer, KeywordNew, TrafficGuardCampaign


class LoadKeywords(LoginRequiredMixin, View):
    """
    Loads a list of keywords based on a campaign ID.

    Return:
        JsonResponse: List of keywords.
    """

    def get(self, request):
        campaign_id = request.GET.get("campaign_id")
        container_id = request.GET.get("container_id")
        all_keywords_for_category = request.GET.get("all_keywords_for_category")

        if campaign_id != "null":
            try:
                campaign = TrafficGuardCampaign.objects.get(id=campaign_id)

                # Get categories associated with the campaign
                categories = campaign.categories.all()

                # Get all keywords for the categories associated with the campaign
                all_keywords = KeywordNew.objects.filter(category__in=categories)
                keywords = list(all_keywords.values("id", "keyword"))

                return JsonResponse(keywords, safe=False)

            except TrafficGuardCampaign.DoesNotExist:
                return JsonResponse({"error": f"No campaign found with id: {campaign_id}"})

        try:
            # Retrieve the AdContainer object using the container_id
            ad_container = AdContainer.objects.get(id=container_id)

            if all_keywords_for_category == "true":
                # Get the TrafficGuardCampaign associated with the AdContainer
                tg_campaign = ad_container.tg_campaign

                # Get categories associated with the TrafficGuardCampaign
                categories = tg_campaign.categories.all()

                # Get all keywords for the categories associated with the campaign
                all_keywords = KeywordNew.objects.filter(category__in=categories)
                keywords = list(all_keywords.values("id", "keyword"))

            else:
                # Retrieve keywords associated with the AdContainer
                keywords = list(
                    KeywordNew.objects.filter(adcontainer=ad_container)
                    .values("id", "keyword")
                )

            return JsonResponse(keywords, safe=False)

        except AdContainer.DoesNotExist:
            return JsonResponse({"error": f"No AdContainer found for the container with id: {container_id}"})
