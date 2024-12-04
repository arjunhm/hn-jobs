from django.urls import path

from company import views

urlpatterns = [
    path("author/list/", views.AuthorListAPI.as_view(), name="author-list"),
    path("author/post/", views.AuthorPostAPI.as_view(), name="author-post-list"),
    path("company/list/", views.CompanyListAPI.as_view(), name="company-list"),
    path("company/post/", views.CompanyPostAPI.as_view(), name="company-post-list"),
]
