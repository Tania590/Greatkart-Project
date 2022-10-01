from django.contrib import admin
from .models import Payment, Order, OrderedProduct

class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    extra = 0
    readonly_fields = ('payment','user','product','variations','quantity','product_price','ordered',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number','full_name','email','phone_number','city','order_total','tax','status','date_modified','is_ordered')
    list_filter = ('status','is_ordered',)
    search_fields = ('order_number','first_name','last_name','phone_number','email',)
    list_per_page = 10
    inlines = [
        OrderedProductInline
    ]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderedProduct)
