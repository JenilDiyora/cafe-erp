from django.urls import path
from .views import ReviewsView

app_name = 'reviews'

urlpatterns = [
    path('', ReviewsView.as_view(), name='list'),
]

