"""
Main URL configuration for the project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    # Root redirect to properties
    path('', RedirectView.as_view(url='/properties/', permanent=False), name='root'),
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # Properties app URLs
    # All URLs starting with /properties/ go to properties.urls
    path('properties/', include('properties.urls')),
]
