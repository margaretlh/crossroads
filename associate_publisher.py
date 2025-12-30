from rest_framework import serializers

class AssociatePublisher(serializers.Serializer):
    publisher_id = serializers.IntegerField(
        required=True
    )
