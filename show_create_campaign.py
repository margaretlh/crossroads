from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib.auth.models import User


class ShowCreateCampaign(LoginRequiredMixin, View):
    """
    A page for creating a new sponsored links campaign.

    Args:
        user_id(int): Publisher ID.

    Return:
        TemplateResponse
    """

    def get(
        self, request, user_id, template="sponsored-links/create-campaign.html"
    ) -> TemplateResponse:

        user = User.objects.get(id=user_id)

        return TemplateResponse(
            request,
            template=template,
            context={"publisher_id": user_id, "publisher_name": user.username},
        )
