from django.db import models
from django.urls import reverse
from category.models import Category


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    is_available = models.BooleanField(default=True)
    stock = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=500)
    image = models.ImageField(upload_to='images/products/')


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'category_slug':self.category.slug, 'product_slug':self.slug})
