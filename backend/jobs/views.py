from django.db.models import Q
from rest_framework import views
from rest_framework.response import Response

from core.mixins import StandardPaginationMixin
from core.pagination import StandardPagination
from jobs.models import Post
from jobs.serializers import PostSerializer


class PostListAPI(views.APIView, StandardPaginationMixin):
    pagination_class = StandardPagination
    serializer_class = PostSerializer

    def get(self, request):
        month = request.GET.get("month")
        year = request.GET.get("year")

        # ! add filters
        queryset = Post.objects.filter(Q(month=month) & Q(year=year))

        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class PostDetailAPI(views.APIView):
    serializer_class = PostSerializer

    def put(self, request):
        id = request.data.get("id")
        status = request.data.get("status")

        try:
            post = Post.objects.get(id=id)
        except:
            return Response({"error": "Post not found"}, status=404)

        post.status = status
        post.save()

        return Response({"success": True}, status=200)
