from rest_framework import serializers

from jobs.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["link"]
