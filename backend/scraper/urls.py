from django.urls import path

from scraper import views

urlpatterns = [
    path("scrape/", views.scrape_data, name='scrape-data'),
]
