from django.urls import include, re_path, path
from rest_framework import routers
from .apis.model import ModelViewSet
from .apis.triton import TritonServerViewSet

router = routers.DefaultRouter()
router.register("model", ModelViewSet, basename='model')
router.register("server", TritonServerViewSet, basename='server')

urlpatterns = [
    path("", include(router.urls)),
]   