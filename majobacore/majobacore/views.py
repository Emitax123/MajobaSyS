from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def majoba_view(request):
    return render(request, 'majoba_template.html')