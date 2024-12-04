from django.shortcuts import render
from django.http import HttpResponse

from scraper.hnscraper import Scraper


def scrape_data(request):
    scraper = Scraper("https://news.ycombinator.com/item?id=42297424")
    scraper.run()
    return HttpResponse({"status": 200})

