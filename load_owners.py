from django.http import JsonResponse
from django.views import View

from django.contrib.auth.models import User

class LoadOwners(View):
    """
    Retrieves all users and returns them in a format
    suitable for select input dropdown presentation.
    """
    def get(self, request):
        users = User.objects.values("id", "username").distinct().order_by("username")
        users_list = [{"name": user["username"], "value": user["id"]} for user in users]

        return JsonResponse(users_list, safe=False)
