from django.shortcuts import render
from django.http import HttpResponse, QueryDict

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __hash__(self):
        return hash((self.username, self.email))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

cur_user = User('joe', 'test')
users = set()

# Create your views here.
def index(request):
    if request.method == 'PUT':
        print(request.body)
        data = QueryDict(request.body)
        cur_user.username = data.get('username')
        cur_user.email = data.get('email')
        new_user = User(cur_user.username, cur_user.email)
        users.add(new_user)

    return render(request, 'argue/index.html', { 'username': cur_user.username, 'email': cur_user.email, 'users': users })

def clicked(request):
    return HttpResponse('You clicked me!')

def edit(request):
    
    return render(request, 'argue/edit.html', { 'username': cur_user.username, 'email': cur_user.email, 'users': users })
