import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.admin._trafficguard.decorators import json_form_request
from apps.sponsored_links import fileutils
from apps.sponsored_links.forms.update_template_request import UpdateTemplateRequest
from apps.sponsored_links_reporting.models import Template

LOGGER = logging.getLogger(__name__)


@method_decorator(json_form_request(UpdateTemplateRequest), name="dispatch")
class UpdateTemplate(LoginRequiredMixin, View):
    """
    Updates a template.

    Args:
        form_payload(dict): Json Form Request.

    Return:
        JsonResponse: success or error message.
    """
    def put(self, request, form_payload) -> JsonResponse:

        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            template = Template.objects.get(id=int(data.get("id")))
            new_owner = data.get("owner")

            template.name = data.get("name", template.name)
            template.filename = data.get("filename", template.filename)
            template.path = data.get("path", template.path)
            template.width = data.get("width", template.width)
            template.height = data.get("height", template.height)
            template.links = data.get("number_of_links", template.links)
            template.private = data.get("private", "false").lower() == "true"

            template.snippet_variables = data.get("variables", template.snippet_variables)
            template.snippet = data.get("snippet", template.snippet)

            if new_owner:
                template.owner = User.objects.get(id=int(new_owner))
            else:
                template.owner = template.owner

            html = data.get("html")

            if html:
                try:
                    fileutils.upload_to_s3_raw(html, template.path)
                except Exception as ex:
                    LOGGER.error(f"Error uploading file to S3: {ex}")
                    return JsonResponse({"error": "Failed to upload file to S3."}, status=500)

            template.save()

            return JsonResponse({"success": "Template updated successfully."}, status=200)

        except Template.DoesNotExist:
            return JsonResponse({"error": "Template not found."}, status=402)

        except Exception as ex:
            print("other error : ",ex)
            return JsonResponse({"error": str(ex)}, status=500)
