import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdContainer

LOGGER = logging.getLogger(__name__)


class CloneZoneAd(LoginRequiredMixin, View):
    """
    Clones a zone ad with new ad name and title.

    Return:
        JsonResponse: success or error message.
    """
    def post(self, request) -> JsonResponse:

        try:
            body_unicode = request.body.decode("utf-8")
            data = json.loads(body_unicode)

            new_name = data.get("name")
            new_title = data.get("title")

            # Safety return - do not run until mock campaigns are cleared for testing
            return

            original_ad = AdContainer.objects.get(id=int(data.get("id")))

            new_ad = AdContainer()
            fields = [field.name for field in AdContainer._meta.fields if field.name != "id"]

            for field in fields:
                setattr(new_ad, field, getattr(original_ad, field))

            new_ad.name = new_name
            new_ad.title = new_title

            new_ad.save()

            return JsonResponse({"success": "Zone ad was cloned successfully."}, status=200)

        except AdContainer.DoesNotExist:
            return JsonResponse({"error": "Zone ad not found."}, status=402)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
