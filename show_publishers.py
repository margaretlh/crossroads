from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse


class ShowPublishers(LoginRequiredMixin, View):
    """
    Shows a list of publishers that have sponsored links campaigns.

    Return:
        TemplateResponse
    """

    def get(self, request, template="sponsored-links/publishers.html") -> TemplateResponse:
        return TemplateResponse(request, template=template)
