from apps.blog.models import Category


def get_context_categories(request):
    categories = Category.objects.all()
    return {"categories": categories}
