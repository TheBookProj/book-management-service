from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
import requests

@api_view(['GET'])
def search_for_books(request):
    user_query = request.GET.get("q", "").replace(" ", "+")
    url = f"{settings.OPEN_LIBRARY_API["API_BASE_URL"]}/search.json?q={user_query}&fields=key,cover_i,title,author_name,ratings_average&limit={settings.OPEN_LIBRARY_API["API_MAX_RESULTS"]}"

    resp = requests.get(url)
    data = resp.json()["docs"]
    books = []

    for book in data:
        # Skipping books that don't have covers
        if 'cover_i' not in book:
            continue

        books.append({
            "key": book["key"],
            "title": book["title"] if "title" in book else "",
            "authors": book["author_name"] if "author_name" in book else [],
            "cover": f"https://covers.openlibrary.org/b/id/{book['cover_i']}-L.jpg",
            "rating": book["ratings_average"] if "ratings_average" in book else -1
        })
    
    return JsonResponse(books, status=200, safe=False)