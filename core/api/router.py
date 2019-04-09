from rest_framework.routers import DefaultRouter

from core.api.history.viewsets import get_history_viewset


class HiddenRouter(DefaultRouter):
    include_root_view = False


class HistorizedRouter(DefaultRouter):
    history_router = None

    def __init__(self, *args, **kwargs):
        self.history_router = HiddenRouter()
        super(HistorizedRouter, self).__init__(*args, **kwargs)

    def register_history_viewset(self, prefix, viewset, basename,
                                 base_name):
        history_viewset = get_history_viewset(viewset)
        history_prefix = f'{prefix}/history'
        history_basename = None
        if basename:
            history_basename = f'{basename}_history'
        self.history_router.register(
            history_prefix, history_viewset, history_basename, base_name)

    def register(self, prefix, viewset, basename=None, base_name=None):
        if getattr(viewset, 'allow_history', True):
            self.register_history_viewset(prefix, viewset, basename, base_name)
        super().register(prefix, viewset, basename, base_name)

    def get_urls(self):
        return self.history_router.get_urls() + super().get_urls()


class StandardizedRouter(HistorizedRouter):
    pass


class StandardizedHiddenRouter(HiddenRouter, HistorizedRouter):
    pass
