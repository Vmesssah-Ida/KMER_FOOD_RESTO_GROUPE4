from django.shortcuts import render


def index(request1):
    return render(request1,"acceuil.html") 

def menu(request2):
    return render(request2,"menu.html") 

def apropos(request3):
    return render(request3,"apropos.html") 