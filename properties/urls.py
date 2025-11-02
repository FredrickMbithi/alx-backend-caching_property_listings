"""
URL configuration for properties app.
"""

from django.urls import path
from . import views

# App namespace (optional but recommended)
app_name = 'properties'

urlpatterns = [
    # Cached property list
    properties/
    path('', views.property_list, name='property_list'),
    
    # Non-cached property list (for testing)
    # URL: /properties/no-cache/
    path('no-cache/', views.property_list_no_cache, name='property_list_no_cache'),
]
