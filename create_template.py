import json
import logging
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from apps.admin._trafficguard.decorators import json_form_request
from apps.sponsored_links import fileutils
from apps.sponsored_links.forms.create_template_request import CreateTemplateRequest
from apps.sponsored_links_reporting.models import Template

LOGGER = logging.getLogger(__name__)


@method_decorator(json_form_request(CreateTemplateRequest), name="dispatch")
class CreateTemplate(LoginRequiredMixin, View):
    """
    Creates a template.

    Return:
        JsonResponse: success or error message.
    """
    def post(self, request, form_payload) -> JsonResponse:
        data = json.loads(request.body.decode('utf-8'))

        # Generate a unique filename using a timestamp
        timestamp = round(time.time() * 1000)
        filename = f'{timestamp}.html'

        # Generate path based on filename
        path = f"templates/{filename}"

        html = data.get("html")

        # Create a new Template object
        template = Template(
            name=data.get("name"),
            created_by=request.user,
            filename=filename,
            path=path,
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            links=int(data.get("links", 0)),
            private=data.get("private", False),
            owner_id=data.get("owner"),
            snippet_id=data.get("snippet"),
            snippet_variables=data.get("variables")
        )

        # Attempt to upload the HTML to S3
        try:
            if html:
                fileutils.upload_to_s3_raw(html, path)

        except Exception as ex:
            LOGGER.error(f"Error uploading file to S3: {ex}")
            return JsonResponse({"error": "Failed to upload file to S3."}, status=500)

        template.save()

        return JsonResponse({"success": "Template created successfully."}, status=201)
