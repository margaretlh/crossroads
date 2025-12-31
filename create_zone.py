import json
from django.http import JsonResponse
from django.views import View
from apps.sponsored_links_reporting.models import AdZone
class CreateZone(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            new_zone = AdZone.objects.create(
                site_id=data["site_id"],
                name=data["name"],
                width=data["width"],
                height=data["height"],
                optimize_ads=data.get("optimize_ads", False),
                optimize_after_clicks=data.get("optimize_after_clicks", 0),
                optimize_go_back_days=data.get("optimize_go_back_days", 0),
                optimize_ad_level=data.get("optimize_ad_level", 0),
                optimize_min_waiting_days=data.get("optimize_min_waiting_days", 0),
                snippet_code=data["snippet_code"]
            )

            new_zone.save()

            return JsonResponse({"success": "Zone created successfully.", "id": new_zone.id}, status=201)

        except Exception as ex:
            print("failure to create zone: ", ex)
            return JsonResponse({"error": str(ex)}, status=500)
