from django.core.paginator import Paginator

from yatube.settings import POSTS_TO_PAGE


def page(queryset, request):
    paginator = Paginator(queryset, POSTS_TO_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page
