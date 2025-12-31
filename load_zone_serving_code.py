import logging

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.sponsored_links_reporting.models import AdZone
from apps.main_app.providers.adspeed import get_zone_serving_code

LOGGER = logging.getLogger(__name__)


class LoadZoneServingCode(LoginRequiredMixin, View):
    """
    Retrieves the zone serving code from Ad Speed and returns it.

    Return:
        JsonResponse: html content
    """
    def get(self, request) -> JsonResponse:

        zone_id = int(request.GET.get("zone_id"))
        format = request.GET.get("format")

        if not zone_id:
            return JsonResponse({"error": "Zone ID not provided."}, status=400)

        try:
            ad_zone = AdZone.objects.get(id=zone_id)
            serving_code = get_zone_serving_code(ad_zone, format)

            return HttpResponse(serving_code, content_type="text/html")

        except Exception as ex:
            LOGGER.error(f"Error retrieving serving code: {ex}")
            return JsonResponse({"error": str(ex)}, status=500)
