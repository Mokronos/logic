from django.shortcuts import render
from django.http import HttpResponse, QueryDict
from argue.models import Axiom, Argument, Premise, Conclusion
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(redirect_field_name='home', login_url='login')
def index(request):
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "base.html"

    if request.method == 'PUT':
        print(f"PUT: {request.body}")
        data = QueryDict(request.body)
        new_axiom = Axiom()
        # need validation here
        new_axiom.name = data.get('name')
        new_axiom.content = data.get('content')
        new_axiom.owner = request.user

        try:
            new_axiom.save()
            print("Saved new axiom")
            for axiom in Axiom.objects.all():
                print(axiom.name)
        except:
            print("Axiom already exists")

    response = render(request, 'argue/index.html', { 'axioms': Axiom.objects.all(),
                                                     'base_template': base_template })
    return response

@login_required
def add(request):
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "base.html"
    response = render(request, 'argue/add.html', { 'axioms': Axiom.objects.all(),
                                                    'base_template': base_template })
    return response

@login_required
def delete(request, id):
    if request.method == 'DELETE':
        print(f"DELETE: {request.body}")
        try:
            Axiom.objects.get(id=id).delete()
            return HttpResponse("", status=200)
        except:
            print("Axiom does not exist")


def overview(request):
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "base.html"
    response =  render(request, 'argue/overview.html', { 'base_template': base_template,
                                                        'premises': Premise.objects.all(),
                                                        'conclusions': Conclusion.objects.all()})
    return response

