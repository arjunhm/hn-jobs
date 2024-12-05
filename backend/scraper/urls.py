from django.urls import path

from scraper import views

urlpatterns = [
    path("run/", views.RunScraper.as_view(), name="scrape-data"),
]
