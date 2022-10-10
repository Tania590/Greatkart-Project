from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account
from  django.db.models import Avg, Count

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

    def calculate_average(self, avg=0):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(avg_rating=Avg('rating'))
        if reviews['avg_rating'] != None:
            avg = reviews['avg_rating']
        return avg

    def count_review(self, review_count=0):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        if reviews['count'] != None:
            review_count = reviews['count']
        return review_count


class VariationManager(models.Manager):
    def all(self):
        return super().all().filter(is_active=True)

    def colors(self):
        return self.all().filter(variation_category='color')

    def sizes(self):
        return self.all().filter(variation_category='size')



class Variation( models.Model):

    VARIATION_CATEGORY_CHOICE = (
        ('color', 'color'),
        ('size', 'size'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=VARIATION_CATEGORY_CHOICE)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    date_modified = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

    class Meta:
        ordering = ('date_modified',)

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
