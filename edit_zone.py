import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdZone

LOGGER = logging.getLogger(__name__)

class EditZone(LoginRequiredMixin, View):
    """
    Edits an AdZone.

    Return:
        JsonResponse: success or error message.
    """
    def put(self, request) -> JsonResponse:
        try:
            data = json.loads(request.body)

            zone = AdZone.objects.get(id=int(data.get("id")))
            new_owner = data.get("owner")

            zone.name = data.get("name", zone.name)
            zone.width = data.get("width", zone.width)
            zone.height = data.get("height", zone.height)
            zone.optimize_ads = data.get("optimize_ads", zone.optimize_ads)
            zone.optimize_after_clicks = data.get("optimize_after_clicks", zone.optimize_after_clicks)
            zone.optimize_go_back_days = data.get("optimize_go_back_days", zone.optimize_go_back_days)
            zone.optimize_min_waiting_days = data.get("optimize_min_waiting_days", zone.optimize_min_waiting_days)
            zone.optimize_ad_level = data.get("optimize_ad_level", zone.optimize_ad_level)
            zone.snippet_code = data.get("snippet_code", zone.snippet_code)

            if new_owner:
                zone.owner = User.objects.get(id=int(new_owner))

            zone.save()
            return JsonResponse({"success": "Zone updated successfully."}, status=200)

        except AdZone.DoesNotExist:
            return JsonResponse({"error": "Zone not found."}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"error": "Owner not found."}, status=404)

        except Exception as ex:
            LOGGER.error(f"Unhandled exception: {ex}")
            return JsonResponse({"error": str(ex)}, status=500)
