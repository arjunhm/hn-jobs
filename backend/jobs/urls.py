from django.urls import path

from jobs import views

urlpatterns = [
    path("list/", views.PostListAPI.as_view(), name="post-list"),
]
