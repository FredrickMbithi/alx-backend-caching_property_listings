"""
Property model for the listing application.

This model represents a real estate property with details like
title, description, price, and location.
"""

from django.db import models


class Property(models.Model):
    """
    Represents a property listing.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.title} - ${self.price}"

from django.db import models


class Property(models.Model):
    """
    Represents a property listing.
    
    Think of this as a form template - every property must have:
    - A title (like "Luxury Beach House")
    - A description (details about the property)
    - A price (how much it costs)
    - A location (where it is)
    - Created timestamp (when it was listed)
    """
    
    # Title of the property (max 200 characters)
    # Example: "Luxury 3BR Apartment in Downtown"
    title = models.CharField(max_length=200)
    
    # Detailed description (unlimited length)
    # Example: "Beautiful apartment with ocean views..."
    description = models.TextField()
    
    # Price in decimal format (max 99999999.99)
    # max_digits=10 means total digits (including decimals)
    # decimal_places=2 means 2 digits after decimal point
    # Example: 125000.50
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Location (max 100 characters)
    # Example: "Miami, FL"
    location = models.CharField(max_length=100)
    
    # Timestamp when property was created
    # auto_now_add=True means Django sets this automatically on creation
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """
        Meta options for the model.
        """
        # Order properties by newest first (- means descending)
        ordering = ['-created_at']
        
        # Human-readable names
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        """
        String representation of the property.
        This is what you see in Django admin and logs.
        """
        return f"{self.title} - ${self.price}"