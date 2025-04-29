from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
import requests

@api_view(['GET'])
def search_for_books(request):
    try:
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
    except:
        return JsonResponse({"error_msg":"Server error"}, status=500)

@api_view(['GET'])
def get_book(request):
    try:
        key = request.GET.get("key", "")
        if not key:
            return JsonResponse({"error_msg": "No key provided"}, status=400)
        url = f"{settings.OPEN_LIBRARY_API["API_BASE_URL"]}/api/get?key={key}"
        
        resp = requests.get(url)
        data = resp.json()

        if data["status"] != "ok":
            return JsonResponse({"error_msg": "Error with API"}, status=500) 
        
        data = data["result"]
        book = {}
        if "description" in data:
            if "value" in data["description"] and data["description"]["type"] == "/type/text":
                book["description"] = data["description"]["value"]
            elif type(data["description"]) == str:
                book["description"] = data["description"]
        else:
            book["description"] = ""

        book["subjects"] = [subject for subject in data["subjects"] if subject[0].isupper()] if "subjects" in data else []
        book["covers"] = [f"https://covers.openlibrary.org/b/id/{cover}-L.jpg" for cover in data["covers"]] if "covers" in data else []

        url = f"{settings.OPEN_LIBRARY_API["API_BASE_URL"]}/{key}/ratings.json"
        resp = requests.get(url)
        data = resp.json()
        book["rating"] = data["summary"]["average"] if "summary" in data and "average" in data["summary"] else -1

        return JsonResponse(book, status=200, safe=False)
    except:
        return JsonResponse({"error_msg": "Server error"}, status=500)
