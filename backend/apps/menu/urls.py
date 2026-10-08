from django.urls import path
from .views import MenuView

app_name = 'menu'

urlpatterns = [
    path('', MenuView.as_view(), name='list'),
]

