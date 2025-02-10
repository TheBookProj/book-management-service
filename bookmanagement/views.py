from django.shortcuts import render
from django.conf import settings
import requests

def search_for_books(request):
    user_query = request.GET.get("q", "")
    user_query = user_query.replace(" ", "+")
    url = f"{settings.API_BASE_URL}/volumes/q={user_query}&maxResults={settings.API_MAX_RESULTS}&key={settings.API_API_KEY}"

    resp = requests.get(url)
    books = resp.json()["items"]