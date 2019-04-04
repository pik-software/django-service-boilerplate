from rest_framework.routers import DefaultRouter

from core.api.history.viewsets import get_history_viewset


class HiddenRouter(DefaultRouter):
    include_root_view = False


class HistorizedRouter(DefaultRouter):
    history_router = None

    def __init__(self, *args, **kwargs):
        self.history_router = HiddenRouter()
        super(HistorizedRouter, self).__init__(*args, **kwargs)

    def register_history_viewset(self, orign_prefix, orig_viewset, orig_name):
        viewset = get_history_viewset(orig_viewset)
        prefix = f'{orign_prefix}/history'
        name = None
        if orig_name:
            name = f'{orig_name}_history'
        self.history_router.register(prefix, viewset, name)

    def register(self, prefix, viewset, base_name=None):
        if getattr(viewset, 'allow_history', True):
            super().register(prefix, viewset, base_name)
        self.register_history_viewset(prefix, viewset, base_name)

    def get_urls(self):
        return self.history_router.get_urls() + super().get_urls()


class StandardizedRouter(HistorizedRouter):
    pass


class StandardizedHiddenRouter(HiddenRouter, HistorizedRouter):
    pass
