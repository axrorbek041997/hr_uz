from django.urls import path
from . import views

urlpatterns = [
    path('', views.payme, name="payme"),
    path('verify/', views.payme_verify, name='payme_verify'),
]