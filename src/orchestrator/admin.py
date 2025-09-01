from django.contrib import admin
from .models import TritonServer, Model, ModelVersion, Tag

# Register your models here.
admin.site.register(TritonServer)
admin.site.register(Model)
admin.site.register(ModelVersion)
admin.site.register(Tag)