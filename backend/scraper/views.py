from rest_framework import views
from rest_framework.response import Response

from scraper.hn_scraper import Scraper


def scrape_data(request):
    request.GET.get("url")
    scraper = Scraper("https://news.ycombinator.com/item?id=42297424")
    scraper.run()
    return HttpResponse({"status": 200})


class RunScraper(views.APIView):
    def post(self, request):
        url = request.data.get("url")
        if url is None:
            return Response({"error": "Invalid URL"}, status=404)

        scraper = Scraper(url)

        success = scraper.run()
        if success is True:
            return Response({"success": True}, status=200)
        return Resposne({"success": False}, status=400)
