from django.db import models
import uuid

# Yeh ek Abstract Model hai. Iska table nahi banega, 
# bas doosre models isse inherit karenge. (DRY Principle)
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class School(TimeStampedModel):
    # UUID isliye taaki URL me school ki ID guess na ki ja sake (Security)
    # Lekin abhi simple ID rakhte hain for simplicity if you prefer.
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, help_text="Unique URL identifier, e.g., ummeed-academy")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    
    # Subscription Logic
    is_active = models.BooleanField(default=True)
    subscription_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name