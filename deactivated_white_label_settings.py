from rest_framework import serializers

class DeactivatedWhiteLabelSettings(serializers.Serializer):
    name = serializers.CharField(
        required=True
    )
    
    title = serializers.CharField(
        required=True
    )

    deactivation_date = serializers.DateField(
        required=True,  # deactivation_date is optional for the PUT or PATCH method
        input_formats=['%Y-%m-%d'],  # Specify acceptable date formats (e.g., 'YYYY-MM-DD')
        allow_null=True  # Allow null value if not provided
    )