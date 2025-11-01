"""
Views for the properties app.

This module contains view functions that handle HTTP requests
and return HTTP responses.
"""

from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property
import logging

logger = logging.getLogger(__name__)


@cache_page(60 * 15)  # Cache for 15 minutes (900 seconds)
def property_list(request):
    """
    Display list of all properties.
    
    This view is cached for 15 minutes using @cache_page decorator.
    
    How it works:
    1. First request: Django fetches data from PostgreSQL, serializes to JSON,
       saves response in Redis, returns to user (SLOW - ~100ms)
    
    2. Subsequent requests (within 15 min): Django gets cached response
       from Redis, returns immediately (FAST - ~5ms)
    
    3. After 15 minutes: Cache expires, process repeats from step 1
    
    Args:
        request: HTTP request object
    
    Returns:
        JSON response with property data
    """
    logger.info("property_list view called - checking cache...")
    
    # This query will run ONLY if response is not in cache
    properties = Property.objects.all().order_by('-created_at')
    
    # Convert queryset to list of dictionaries
    properties_data = list(properties.values(
        'id', 'title', 'description', 'price', 'location', 'created_at'
    ))
    
    logger.info(f"Fetched {len(properties_data)} properties from database")
    
    # Return JSON response
    return JsonResponse({
        'properties': properties_data,
        'count': len(properties_data)
    })


def property_list_no_cache(request):
    """
    Same view WITHOUT caching (for comparison/testing).
    
    This always hits the database - useful for:
    - Testing cache effectiveness
    - Comparing performance
    - Admin/debugging purposes
    """
    logger.info("property_list_no_cache called - no caching")
    
    properties = Property.objects.all().order_by('-created_at')
    property_count = properties.count()
    
    context = {
        'properties': properties,
        'property_count': property_count,
        'no_cache': True,  # Flag to show in template
    }
    
    return render(request, 'properties/property_list.html', context)