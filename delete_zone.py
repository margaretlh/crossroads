from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import AdZone


class DeleteZone(LoginRequiredMixin, View):
    """
    Deletes an ad container.

    Return:
        JsonResponse: success or error message.
    """
    def delete(self, request) -> JsonResponse:

        zone_id = request.GET.get("id")

        if not zone_id:
            return JsonResponse({"error": "Zone ID not provided."}, status=400)

        try:
            site = AdZone.objects.get(id=int(zone_id))
            site.deleted = True
            site.save()
            return JsonResponse({"success": "Zone deleted successfully."}, status=200)

        except AdZone.DoesNotExist:
            return JsonResponse({"error": "Zone not found."}, status=404)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
