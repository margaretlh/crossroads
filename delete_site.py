from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import Site


class DeleteSite(LoginRequiredMixin, View):
    """
    Deletes a site.

    Return:
        JsonResponse: success or error message.
    """
    def delete(self, request):
        site_id = request.GET.get("id")
        if not site_id:
            return JsonResponse({"error": "Site ID not provided."}, status=400)

        try:
            site = Site.objects.get(id=site_id)
            site.deleted = True
            site.save()
            return JsonResponse({"success": "Site deleted successfully."}, status=200)

        except Site.DoesNotExist:
            return JsonResponse({"error": "Site not found."}, status=404)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
