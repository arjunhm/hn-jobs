from django.shortcuts import render
from rest_framework import generics, views
from rest_framework.response import Response

from company.models import Author, Company
from company.serializers import AuthorSerializer, CompanySerializer

class AuthorListAPI(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class CompanyListAPI(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

