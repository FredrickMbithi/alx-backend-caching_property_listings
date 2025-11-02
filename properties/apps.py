"""
App configuration for properties app.
"""

from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    """
    Configuration class for the properties app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    verbose_name = 'Property Listings'
    
    def ready(self):
        """
        Called when Django starts.
        
        This is where we import signal handlers to register them.
        Signals must be imported here (not at module level) to avoid
        circular imports and ensure they're registered at startup.
        
        IMPORTANT: This method runs every time Django loads the app,
        including management commands. Make sure signal handlers are
        idempotent (safe to register multiple times).
        """
        # Import signal handlers
        # This registers the @receiver decorators
        import properties.signals  # noqa: F401