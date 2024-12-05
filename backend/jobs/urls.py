from django.urls import path

from jobs import views

urlpatterns = [
    path("list/", views.PostListAPI.as_view(), name="post-list"),
    path("detail/", views.PostListAPI.as_view(), name="post-detail"),
    path("meta/", views.HNLinkAPI.as_view(), name="meta-list"),
]
