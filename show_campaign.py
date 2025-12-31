from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib.auth.models import User


class ShowCampaignManager(LoginRequiredMixin, View):
    """
    Shows the sponsored links campaign manager.

    Args:
        campaign_id(int): Campaign ID.

    Return:
        TemplateResponse
    """

    def get(
        self, request, user_id, campaign_id, template="sponsored-links/campaign.html"
    ) -> TemplateResponse:

        user = User.objects.get(id=user_id)

        return TemplateResponse(
            request,
            template=template,
            context={
                "publisher_id": user_id,
                "publisher_name": user.username,
                "campaign_id": campaign_id,
            },
        )
