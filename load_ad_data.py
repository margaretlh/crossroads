from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from apps.sponsored_links_reporting.models import AdContainer


class LoadAdData(LoginRequiredMixin, View):
    """
    Loads AdContainer data for advanced, compartmentalized editing.

    Return:
        JsonResponse: List of keyword lists.
    """
    def get(self, request):
        container_id = request.GET.get("container_id")

        try:
            # Retrieve the AdContainer object using the container_id
            ad_container = AdContainer.objects.get(id=container_id)

            # Retrieve the Template object associated with the AdContainer
            template = ad_container.template

            ad_data = {
                "container_id": ad_container.id,
                "container_name": ad_container.name,
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "filename": template.filename,
                    "path": template.path,
                    "width": template.width,
                    "height": template.height,
                    "links": template.links,
                    "private": template.private,
                    "owner": template.owner_id,
                    "snippet": template.snippet_id,
                    "snippet_variables": template.snippet_variables
                }
            }

            return JsonResponse(ad_data)

        except AdContainer.DoesNotExist:
            return JsonResponse({"error": f"No AdContainer found for the container with id: {container_id}"})
