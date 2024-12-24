from rest_framework import serializers

from company.models import Author, Company


class AuthorSerializer(serializers.ModelSerializer):
    count = 0
    class Meta:
        model = Author
        fields = ["name", "link", "count"]



class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ["id"]
