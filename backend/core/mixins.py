class StandardPaginationMixin(object):
    @property
    def paginator(self):
        # if paginator has not been set
        if not hasattr(self, "_paginator"):
            # if no pagination class has been provided
            if self.pagination_class is None:
                self._paginator = None
            # set pagination class
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None

        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
