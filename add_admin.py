from rest_framework import serializers

class AddAdmin(serializers.Serializer):
    admin_id = serializers.IntegerField(
        required=True
    )
