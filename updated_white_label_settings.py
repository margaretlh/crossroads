from rest_framework import serializers

class UpdatedWhiteLabelSettings(serializers.Serializer):
    name = serializers.CharField(
        required=True
    )

    title = serializers.CharField(
        required=True
    )

    pay_difference_to_id = serializers.IntegerField(
        required=True
    )
