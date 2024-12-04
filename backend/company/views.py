from django.shortcuts import render
from rest_framework import generics, views
from rest_framework.response import Response

from company.models import Author, Company
from company.serializers import AuthorSerializer, CompanySerializer
from jobs.serializers import PostSerializer


class AuthorListAPI(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class CompanyListAPI(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class AuthorPostAPI(views.APIView):
    serializer_class = PostSerializer

    def get(self, request):
        id = request.GET.get("id")
        try:
            author = Author.objects.get(id=id)
        except:
            return Response({"error": "Author not found"}, status=404)

        posts = author.posts.all()
        serialized_data = self.serializer_class(posts, many=True)

        return Response(serialized_data.data, status=200)


class CompanyPostAPI(views.APIView):
    serializer_class = PostSerializer

    def get(self, request):
        id = request.GET.get("id")
        try:
            company = Company.objects.get(id=id)
        except:
            return Response({"error": "Company not found"}, status=404)

        posts = company.posts.all()
        serialized_data = self.serializer_class(posts, many=True)

        return Response(serialized_data.data, status=200)
