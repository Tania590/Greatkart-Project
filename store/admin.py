from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name','category', 'stock', 'price', 'date_modified', 'is_available')

admin.site.register(Product, ProductAdmin)
