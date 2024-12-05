from rest_framework import serializers

from company.serializers import AuthorSerializer, CompanySerializer
from jobs.models import HNLink, Post


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    company = CompanySerializer()

    class Meta:
        model = Post
        exclude = ["id"]


class PostLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["link"]


class HNLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = HNLink
        exclude = ["id"]
