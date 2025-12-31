import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdZone

LOGGER = logging.getLogger(__name__)


class CloneZone(LoginRequiredMixin, View):
    """
    Clones an ad zone with a new name.

    Return:
        JsonResponse: success or error message.
    """
    def post(self, request) -> JsonResponse:
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Fetch the original AdZone instance
            original_zone = AdZone.objects.get(id=int(data["id"]))

            # Create a clone by setting the id to None and updating the name
            original_zone.id = None
            original_zone.name = data["name"]
            original_zone.save()

            return JsonResponse({"success": "Zone cloned successfully with new name."}, status=201)

        except AdZone.DoesNotExist:
            return JsonResponse({"error": "Original zone not found."}, status=404)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
