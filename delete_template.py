from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import Template


class DeleteTemplate(LoginRequiredMixin, View):
    """
    Deletes a template.

    Return:
        JsonResponse: success or error message.
    """
    def delete(self, request) -> JsonResponse:
        template_id = request.GET.get("template_id")
        if not template_id:
            return JsonResponse({"error": "Template ID not provided."}, status=400)

        try:
            template = Template.objects.get(id=template_id)
            template.deleted = True
            template.save()
            return JsonResponse({"success": "Template deleted successfully."}, status=200)

        except Template.DoesNotExist:
            return JsonResponse({"error": "Template not found."}, status=404)

        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
