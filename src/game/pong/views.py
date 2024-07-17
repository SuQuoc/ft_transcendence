from django.shortcuts import render


def index(request):
    return render(request, "static/pong.html")

""" def room(request, room_name):
    return render(request, "pong/pong.html", {"room_name": room_name}) """
