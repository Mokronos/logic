from django.shortcuts import render
from django.http import HttpResponse, QueryDict

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

user1 = User('joe', 'test')

# Create your views here.
def index(request):
    if request.method == 'PUT':
        print(request.body)
        data = QueryDict(request.body)
        user1.username = data.get('username')
        user1.email = data.get('email')

    return render(request, 'argue/index.html', { 'username': user1.username, 'email': user1.email })

def clicked(request):
    return HttpResponse('You clicked me!')

def edit(request):
    
    return render(request, 'argue/edit.html', { 'username': user1.username, 'email': user1.email })
