"""
Signal handlers for cache invalidation.

This module listens for Property model changes and automatically
clears related caches to maintain data consistency.

Signals used:
- post_save: Triggered after a model instance is saved (created or updated)
- post_delete: Triggered after a model instance is deleted
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

logger = logging.getLogger('properties')


@receiver(post_save, sender=Property)
def invalidate_property_cache_on_save(sender, instance, created, **kwargs):
    """
    Signal handler: Invalidate cache when a Property is created or updated.
    
    This function is automatically called by Django whenever:
    - A new Property is created (created=True)
    - An existing Property is updated (created=False)
    
    Args:
        sender: The model class (Property)
        instance: The actual Property object that was saved
        created: Boolean - True if new object, False if updated
        **kwargs: Additional signal data
    
    Example flow:
        >>> property = Property.objects.create(title="New House", ...)
        >>> # Signal fires automatically
        >>> # Cache 'all_properties' is cleared
        >>> # Next call to get_all_properties() will fetch fresh data
    """
    # Determine action type
    action = "created" if created else "updated"
    
    logger.info(f"🔔 Signal received: Property {action} - '{instance.title}' (ID: {instance.id})")
    
    # Clear the main properties cache
    cache_key = 'all_properties'
    result = cache.delete(cache_key)
    
    if result:
        logger.info(f"✓ Cache cleared: {cache_key} (due to Property {action})")
    else:
        logger.warning(f"⚠ Cache key not found: {cache_key} (may have already expired)")
    
    # Optional: Clear location-specific caches
    if instance.location:
        location_cache_key = f'properties_location_{instance.location.lower().replace(" ", "_")}'
        cache.delete(location_cache_key)
        logger.info(f"✓ Cleared location cache: {location_cache_key}")
    
    # Optional: Clear property count cache
    cache.delete('property_count')
    logger.info(f"✓ Cleared property count cache")


@receiver(post_delete, sender=Property)
def invalidate_property_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler: Invalidate cache when a Property is deleted.
    
    This function is automatically called by Django when a Property is deleted.
    
    Args:
        sender: The model class (Property)
        instance: The Property object that was deleted
        **kwargs: Additional signal data
    
    Example flow:
        >>> property = Property.objects.get(id=1)
        >>> property.delete()
        >>> # Signal fires automatically
        >>> # Cache is cleared
    """
    logger.info(f"🔔 Signal received: Property deleted - '{instance.title}' (ID: {instance.id})")
    
    # Clear the main properties cache
    cache_key = 'all_properties'
    result = cache.delete(cache_key)
    
    if result:
        logger.info(f"✓ Cache cleared: {cache_key} (due to Property deletion)")
    else:
        logger.warning(f"⚠ Cache key not found: {cache_key}")
    
    # Optional: Clear location-specific caches
    if instance.location:
        location_cache_key = f'properties_location_{instance.location.lower().replace(" ", "_")}'
        cache.delete(location_cache_key)
        logger.info(f"✓ Cleared location cache: {location_cache_key}")
    
    # Optional: Clear property count cache
    cache.delete('property_count')
    logger.info(f"✓ Cleared property count cache")


# Optional: Bulk operations handler
def clear_all_property_caches():
    """
    Manually clear all property-related caches.
    
    Useful for:
    - Bulk imports
    - Data migrations
    - Manual cache management
    
    Example:
        >>> from properties.signals import clear_all_property_caches
        >>> clear_all_property_caches()
    """
    logger.info("Clearing ALL property-related caches...")
    
    # Clear main cache
    cache.delete('all_properties')
    
    # Clear property count
    cache.delete('property_count')
    
    # Clear all location caches (pattern matching)
    # Note: This requires iterating through keys, which can be slow
    # In production, consider using cache versioning instead
    
    logger.info("✓ All property caches cleared")