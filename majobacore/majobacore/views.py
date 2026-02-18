from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def majoba_view(request):
    return render(request, 'majoba_template.html')

def hormicons_view(request):
    return render(request, 'hormicons_template.html')

def constructora_view(request):
    return render(request, 'constructora_template.html')

def budget_view(request):
    return render(request, 'budget_form.html')