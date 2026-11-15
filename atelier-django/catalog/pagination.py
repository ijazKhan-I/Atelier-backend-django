from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StrapiPagination(PageNumberPagination):
    page_query_param = "pagination[page]"
    page_size_query_param = "pagination[pageSize]"
    page_size = 25
    max_page_size = 100

    def get_paginated_response(self, data):
        page = self.page
        return Response(
            {
                "data": data,
                "meta": {
                    "pagination": {
                        "page": page.number,
                        "pageSize": self.get_page_size(self.request) or self.page_size,
                        "pageCount": page.paginator.num_pages,
                        "total": page.paginator.count,
                    }
                },
            }
        )

    def get_page_number(self, request, paginator):
        # Also accept plain ?page= for convenience.
        page_number = request.query_params.get(self.page_query_param) or request.query_params.get(
            "page"
        )
        if page_number in (None, "", "last"):
            return super().get_page_number(request, paginator)
        return page_number
