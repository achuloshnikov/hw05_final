from django.core.paginator import Paginator

from yatube.settings import CONSTANT_TOP


def get_page_context(queryset, request):
    paginator = Paginator(queryset, CONSTANT_TOP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
