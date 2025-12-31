import logging

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.sponsored_links import fileutils
from apps.sponsored_links_reporting.models import AdContainer

LOGGER = logging.getLogger(__name__)


class LoadZoneAdHtml(LoginRequiredMixin, View):
    """
    Retrieves the template HTML for the relevant zone ad and returns it.

    Return:
        JsonResponse: html content
    """
    def get(self, request) -> JsonResponse:

        ad_container_id = int(request.GET.get("zone_ad_id"))

        if not ad_container_id:
            return JsonResponse({"error": "Ad Container ID not provided."}, status=400)

        try:
            ad_container = AdContainer.objects.get(id=ad_container_id)

            keywords = ad_container.keywords.all()
            keyword_context = {}

            for idx, keyword in enumerate(keywords):
                keyword_context[f"{{{{links.{idx}.keyword}}}}"] = keyword.keyword

            html = fileutils.get_file(ad_container.template)

            for placeholder, keyword_value in keyword_context.items():
                html = html.replace(placeholder, keyword_value)

            return HttpResponse(html, content_type="text/html")

        except AdContainer.DoesNotExist:

            return JsonResponse({"error": "Ad Container not found."}, status=404)
        except Exception as ex:
            LOGGER.error(f"Error retrieving template HTML for Ad Container: {ex}")
            return JsonResponse({"error": str(ex)}, status=500)
