from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    image = models.ImageField(upload_to='images/categories/', blank=True)
    description = models.TextField(max_length=400, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title
