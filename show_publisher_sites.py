from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib.auth.models import User


class ShowPublisherSites(LoginRequiredMixin, View):
    """
    Shows a list of sites belonging to the publisher.

    Args:
        user_id(int): Publisher ID.

    Return:
        TemplateResponse
    """

    def get(
        self, request, user_id, template="sponsored-links/publisher-sites.html"
    ) -> TemplateResponse:

        user = User.objects.get(id=user_id)

        return TemplateResponse(
            request,
            template=template,
            context={"publisher_id": user_id, "publisher_name": user.username},
        )
