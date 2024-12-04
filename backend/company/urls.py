from django.urls import path

from company import views

urlpatterns = [
    path("author/list/", views.AuthorListAPI.as_view(), name="author-list"),
    path("list/", views.CompanyListAPI.as_view(), name="company-list"),
]
