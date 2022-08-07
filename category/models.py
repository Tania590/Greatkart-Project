from django.db import models
from django.urls import reverse

class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    image = models.ImageField(upload_to='images/categories/', blank=True)
    description = models.TextField(max_length=400, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products_by_category', kwargs={'category_slug':self.slug})
