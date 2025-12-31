from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib.auth.models import User


class ShowTemplates(LoginRequiredMixin, View):
    """
    Shows the sponsored links templates page.

    Return:
        TemplateResponse
    """

    def get(
        self, request, template="sponsored-links/templates.html"
    ) -> TemplateResponse:

        return TemplateResponse(
            request,
            template=template
        )
