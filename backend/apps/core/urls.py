from django.urls import path
from .views import HomeView, AboutView, robots_txt_view, sitemap_xml_view

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('sitemap.xml', sitemap_xml_view, name='sitemap_xml'),
]

