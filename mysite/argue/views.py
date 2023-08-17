from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'argue/index.html')

def clicked(request):
    return HttpResponse('You clicked me!')

def account_edit(request):
    return "test"
