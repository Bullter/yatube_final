from django.core.paginator import Paginator

from .constants import POSTS_PER_PAGE


def paginator(request, posts):
    something = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = something.get_page(page_number)
    return page_obj
