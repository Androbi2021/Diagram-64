from django.urls import path
from .views import GeneratePdfApiView

urlpatterns = [
    path('generate-pdf/', GeneratePdfApiView.as_view(), name='generate-pdf'),
]
