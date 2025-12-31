import logging

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from apps.sponsored_links import fileutils
from apps.sponsored_links_reporting.models import Template

LOGGER = logging.getLogger(__name__)


class LoadTemplateHtml(LoginRequiredMixin, View):
    """
    Retrieves the template HTML from its S3 location and returns it.

    Return:
        JsonResponse: html content
    """
    def get(self, request) -> JsonResponse:

        template_id = int(request.GET.get("template_id"))

        if not template_id:
            return JsonResponse({"error": "Template ID not provided."}, status=400)

        try:
            template = Template.objects.get(id=template_id)
            html = fileutils.get_file(template)

            return HttpResponse(html, content_type="text/html")

        except Template.DoesNotExist:

            return JsonResponse({"error": "Template not found."}, status=404)
        except Exception as ex:
            LOGGER.error(f"Error retrieving template HTML: {ex}")
            return JsonResponse({"error": str(ex)}, status=500)
