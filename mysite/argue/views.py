from django.shortcuts import render
from django.http import HttpResponse, QueryDict
from argue.models import User


cur_user = User(username='default', email='default')

# Create your views here.
def index(request):
    if request.method == 'PUT':
        print(f"PUT: {request.body}")
        data = QueryDict(request.body)
        cur_user.username = data.get('username')
        cur_user.email = data.get('email')
        new_user = User(username=cur_user.username, email=cur_user.email)
        try:
            new_user.save()
        except:
            print("User already exists")

    for user in User.objects.all():
        print(f"User: {user.username}, {user.email}")
    return render(request, 'argue/index.html', { 'username': cur_user.username, 'email': cur_user.email, 'users': User.objects.all() })

def clicked():
    return HttpResponse("You clicked me!")

def edit(request):
    return render(request, 'argue/edit.html', { 'username': cur_user.username, 'email': cur_user.email, 'users': User.objects.all() })

def delete(request, id):
    if request.method == 'DELETE':
        print(f"DELETE: {request.body}")
        try:
            User.objects.get(username=id).delete()
            return HttpResponse("", status=200)
        except:
            print("User does not exist")
            return


