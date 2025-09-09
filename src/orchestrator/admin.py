from django.contrib import admin
from .models import TritonServer, Model, Tag, ModelInstance

# Register your models here.
admin.site.register(TritonServer)
admin.site.register(Model)
admin.site.register(ModelInstance)
admin.site.register(Tag)