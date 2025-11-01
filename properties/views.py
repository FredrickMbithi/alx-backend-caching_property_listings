"""
Views for the properties app.

This module contains view functions that handle HTTP requests
and return HTTP responses.
"""

from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from .models import Property
from .utils import get_all_properties, get_redis_cache_metrics
import logging

logger = logging.getLogger(__name__)


@cache_page(60 * 15)  # Cache for 15 minutes (900 seconds)
def property_list(request):
    """
    Display list of all properties with JSON response.
    
    NOW USES LOW-LEVEL CACHING:
    - @cache_page caches the JSON response (view-level)
    - get_all_properties() caches the QuerySet (data-level)
    
    This provides TWO layers of caching:
    1. View cache (full JSON response) - expires in 15 min
    2. Data cache (QuerySet) - expires in 1 hour
    
    Args:
        request: HTTP request object
    
    Returns:
        JSON response with property data
    """
    logger.info("property_list view called - using low-level cache...")
    
    # Use cached queryset from get_all_properties()
    # This will either return cached data or query database
    properties = get_all_properties()
    
    # Convert to list of dictionaries for JSON serialization
    properties_data = [
        {
            'id': prop.id,
            'title': prop.title,
            'description': prop.description,
            'price': str(prop.price),
            'location': prop.location,
            'created_at': prop.created_at.isoformat() if prop.created_at else None
        }
        for prop in properties
    ]
    
    logger.info(f"Retrieved {len(properties_data)} properties (from cache or DB)")
    
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