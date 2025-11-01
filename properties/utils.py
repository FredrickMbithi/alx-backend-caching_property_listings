"""
Utility functions for caching and cache metrics.

This module provides low-level caching utilities and Redis metrics analysis.
"""

from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property
import logging

logger = logging.getLogger('properties')


def get_all_properties():
    """
    Get all properties with low-level caching.
    
    This function implements a caching pattern:
    1. Check if data exists in Redis cache
    2. If found (cache HIT): Return cached data
    3. If not found (cache MISS): Query database, cache result, return data
    
    Cache key: 'all_properties'
    Cache duration: 1 hour (3600 seconds)
    
    Returns:
        QuerySet: All Property objects ordered by creation date
    
    Example:
        >>> properties = get_all_properties()
        >>> for prop in properties:
        ...     print(prop.title)
    """
    # Define cache key (must be unique and descriptive)
    cache_key = 'all_properties'
    
    # Step 1: Try to get data from Redis cache
    logger.info(f"Checking cache for key: {cache_key}")
    cached_properties = cache.get(cache_key)
    
    # Step 2: If found in cache, return immediately (CACHE HIT)
    if cached_properties is not None:
        logger.info(f"✓ Cache HIT for {cache_key} - returning cached data")
        return cached_properties
    
    # Step 3: If not in cache, fetch from database (CACHE MISS)
    logger.info(f"✗ Cache MISS for {cache_key} - querying database")
    
    # Query database for all properties
    properties = Property.objects.all().order_by('-created_at')
    
    # Convert QuerySet to list (required for caching)
    # Django QuerySets are lazy - they need to be evaluated
    properties_list = list(properties)
    
    logger.info(f"Fetched {len(properties_list)} properties from database")
    
    # Step 4: Store result in Redis cache
    # cache.set(key, value, timeout_in_seconds)
    cache.set(cache_key, properties_list, 3600)  # Cache for 1 hour
    
    logger.info(f"✓ Cached {len(properties_list)} properties with key: {cache_key}")
    
    # Step 5: Return the data
    return properties_list


def clear_properties_cache():
    """
    Manually clear the all_properties cache.
    
    This is useful when:
    - You add/update/delete properties
    - You want to force fresh data
    - Testing cache behavior
    
    Returns:
        bool: True if cache was cleared, False otherwise
    
    Example:
        >>> clear_properties_cache()
        >>> # Next call to get_all_properties() will query database
    """
    cache_key = 'all_properties'
    
    logger.info(f"Clearing cache for key: {cache_key}")
    
    # Delete the cache entry
    result = cache.delete(cache_key)
    
    if result:
        logger.info(f"✓ Cache cleared for key: {cache_key}")
    else:
        logger.warning(f"✗ Cache key not found or already cleared: {cache_key}")
    
    return result


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache performance metrics.
    
    This function connects directly to Redis and extracts performance data:
    - keyspace_hits: Number of successful key lookups
    - keyspace_misses: Number of failed key lookups (key not found)
    - hit_ratio: Percentage of successful lookups
    
    A high hit ratio (>80%) means your cache is effective!
    
    Returns:
        dict: Cache metrics including hits, misses, and hit ratio
    
    Example:
        >>> metrics = get_redis_cache_metrics()
        >>> print(f"Hit Ratio: {metrics['hit_ratio']:.2f}%")
        Hit Ratio: 85.50%
    """
    try:
        # Get direct connection to Redis
        redis_conn = get_redis_connection('default')
        
        # Get Redis INFO stats
        # This contains detailed server statistics
        info = redis_conn.info('stats')
        
        # Extract relevant metrics
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        
        # Calculate total requests
        total_requests = keyspace_hits + keyspace_misses
        
        # Calculate hit ratio (avoid division by zero)
        if total_requests > 0:
            hit_ratio = (keyspace_hits / total_requests) * 100
        else:
            hit_ratio = 0.0
        
        # Prepare metrics dictionary
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': hit_ratio,
            'hit_ratio_formatted': f"{hit_ratio:.2f}%"
        }
        
        # Log metrics
        logger.info("=" * 50)
        logger.info("REDIS CACHE METRICS")
        logger.info("=" * 50)
        logger.info(f"Total Requests: {total_requests:,}")
        logger.info(f"Cache Hits:     {keyspace_hits:,}")
        logger.info(f"Cache Misses:   {keyspace_misses:,}")
        logger.info(f"Hit Ratio:      {hit_ratio:.2f}%")
        logger.info("=" * 50)
        
        # Interpret results
        if hit_ratio >= 80:
            logger.info("✓ EXCELLENT - Cache is highly effective!")
        elif hit_ratio >= 60:
            logger.info("✓ GOOD - Cache is working well")
        elif hit_ratio >= 40:
            logger.info("⚠ FAIR - Consider optimizing cache strategy")
        else:
            logger.info("✗ POOR - Cache needs optimization")
        
        return metrics
    
    except Exception as e:
        logger.error(f"Failed to retrieve cache metrics: {str(e)}")
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0.0,
            'hit_ratio_formatted': '0.00%'
        }


def warm_cache():
    """
    Pre-populate the cache with data (cache warming).
    
    This is useful:
    - After clearing cache
    - After deploying new code
    - During off-peak hours to prepare for traffic
    
    Example:
        >>> warm_cache()
        >>> # Cache is now populated, first users get fast responses
    """
    logger.info("Warming cache - pre-loading data...")
    
    # This will query database and cache the result
    properties = get_all_properties()
    
    logger.info(f"✓ Cache warmed with {len(properties)} properties")
    
    return len(properties)


# Additional utility functions for specific use cases

def get_properties_by_location(location, cache_timeout=1800):
    """
    Get properties filtered by location with caching.
    
    Args:
        location: Location string to filter by
        cache_timeout: Cache duration in seconds (default: 30 minutes)
    
    Returns:
        list: Properties in the specified location
    """
    # Create location-specific cache key
    cache_key = f'properties_location_{location.lower().replace(" ", "_")}'
    
    # Try cache first
    cached = cache.get(cache_key)
    if cached is not None:
        logger.info(f"✓ Cache HIT for location: {location}")
        return cached
    
    # Query database
    logger.info(f"✗ Cache MISS for location: {location} - querying database")
    properties = list(Property.objects.filter(location__icontains=location).order_by('-created_at'))
    
    # Cache result
    cache.set(cache_key, properties, cache_timeout)
    logger.info(f"✓ Cached {len(properties)} properties for location: {location}")
    
    return properties


def get_property_count():
    """
    Get total property count with caching.
    
    Returns:
        int: Total number of properties
    """
    cache_key = 'property_count'
    
    count = cache.get(cache_key)
    if count is not None:
        return count
    
    count = Property.objects.count()
    cache.set(cache_key, count, 3600)  # Cache for 1 hour
    
    return count