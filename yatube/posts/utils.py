from django.core.paginator import Paginator

from yatube.settings import QTY_POSTS_TO_PAGE


def page(queryset, request):
    paginator = Paginator(queryset, QTY_POSTS_TO_PAGE)
    return paginator.get_page(request.GET.get('page'))
