from rest_framework import serializers


class UpdatedCampaignSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    crossroads_user_id = serializers.IntegerField(required=True)
    routing_domain_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    category_ids = serializers.ListField()
    redirection_rules = serializers.ListField()


class NewKeywordList(serializers.Serializer):
    name = serializers.CharField(required=True)
    keywords = serializers.CharField(required=True)
    default_city = serializers.CharField(required=False, allow_blank=True)
    default_metro = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.IntegerField(required=True)
    category_id = serializers.IntegerField(required=True)

class NewCampaign(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False)
    category_id = serializers.IntegerField(required=True)
    sponsored_links_category_id = serializers.IntegerField(required=True)
    redirection_rules = serializers.ListField(required=True)
    routing_domain_id = serializers.IntegerField(required=True)
    keywords = serializers.CharField(required=True, allow_blank=False)
