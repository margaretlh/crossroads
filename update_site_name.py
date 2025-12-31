import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import Site

LOGGER = logging.getLogger(__name__)


class UpdateSiteName(LoginRequiredMixin, View):
    """
    Updates a site name.

    Return:
        JsonResponse: success or error message.
    """
    def put(self, request) -> JsonResponse:

        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            site = Site.objects.get(id=int(data.get("id")))
            new_name = data.get("name")

            site.name = new_name

            site.save()

            return JsonResponse({"success": "Site name updated successfully."}, status=200)

        except Site.DoesNotExist:
            return JsonResponse({"error": "Site not found."}, status=402)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
