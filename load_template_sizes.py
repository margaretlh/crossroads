from django.http import JsonResponse
from django.views import View

from apps.sponsored_links_reporting.models import Template


class LoadTemplateSizes(View):
    """
    Retrieves all pre-existing template size options and returns them
    in a format suitable for select input dropdown presentation.
    """
    def get(self, request):
        sizes = Template.objects.values("width", "height").distinct().order_by("width")
        sizes_list = [{"name": f"{size['width']}x{size['height']}",
                       "value": f"{size['width']}x{size['height']}"}
                       for size in sizes]

        return JsonResponse(sizes_list, safe=False)
