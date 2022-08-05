from .models import Category

def display_category(request):
    categories = Category.objects.all()
    return {'categories':categories}
