from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TritonServer

# Create your views here.
@login_required
def server_view(request):
    servers = TritonServer.objects.all()
    return render(request, 'server.html', {'servers': servers})
