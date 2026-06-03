from django.urls import path
from . import views

urlpatterns = [
    path('chat/client/', views.client_chat, name='ia_client_chat'),
    path('chat/employee/', views.employee_chat, name='ia_employee_chat'),
]