from rest_framework import serializers

from company.models import Author, Company


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        exclude = ["id"]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ["id"]
