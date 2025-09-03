from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TritonServer, Model

# Create your views here.
def server_view(request):
    servers = TritonServer.objects.all()
    return render(request, 'server.html', {'servers': servers})

def model_view(request):
    models = Model.objects.all()
    return render(request, 'model.html', {'models': models})