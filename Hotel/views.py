from django.shortcuts import render

def glowna(request):
    return render(request, "hotel/index.html")