from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdContainer


class DeleteZoneAd(LoginRequiredMixin, View):
    """
    Deletes an ad container.

    Return:
        JsonResponse: success or error message.
    """
    def delete(self, request) -> JsonResponse:

        ad_container_id = request.GET.get("id")

        # Safety return - do not run until mock campaigns are cleared for testing
        return

        if not ad_container_id:
            return JsonResponse({"error": "Zone Ad ID not provided."}, status=400)

        try:
            site = AdContainer.objects.get(id=int(ad_container_id))
            site.deleted = True
            site.save()
            return JsonResponse({"success": "Zone Ad deleted successfully."}, status=200)

        except AdContainer.DoesNotExist:
            return JsonResponse({"error": "Zone Ad not found."}, status=404)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
