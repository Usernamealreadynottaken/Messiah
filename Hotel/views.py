from django.shortcuts import render

from Hotel.models import Pokoj, Rezerwacja


def glowna(request):
    return render(request, "hotel/index.html")


def rezerwacje(request):
    context = {}
    return render(request, "hotel/rezerwacje.html")