from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page=9):
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_prefix = query_params.urlencode()
    if query_prefix:
        query_prefix += "&"
    return page_obj, query_prefix
