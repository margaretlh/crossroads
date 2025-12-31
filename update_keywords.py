import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdContainer, KeywordNew


class UpdateKeywords(LoginRequiredMixin, View):
    """
    Loads a list of keywords based on a campaign ID.

    Return:
        JsonResponse: List of keywords.
    """

    def post(self, request):

        try:
            payload = json.loads(request.body)
            container_id = payload.get("container_id")
            keywords_string = payload.get("keywords")

            ad_container = AdContainer.objects.get(id=container_id)

            # Split the keywords string into individual keywords
            keywords_list = keywords_string.split('\n')

            excluded_keywords = ad_container.keywords.exclude(keyword__in=keywords_list)

            for keyword in excluded_keywords:
                ad_container.keywords.remove(keyword)

            return JsonResponse({"success": "Keywords updated successfully"})

        except AdContainer.DoesNotExist:
            return JsonResponse({"error": f"No AdContainer found for the ID: {container_id}"})
        except Exception as e:
            return JsonResponse({"error": str(e)})
