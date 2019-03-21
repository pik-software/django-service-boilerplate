from corsheaders.middleware import CorsMiddleware

from pik.core.cache import cachedmethod

from .consts import CACHE_KEY, DEFAULT_CACHE_NAME


class CachedCorsMiddleware(CorsMiddleware):
    @cachedmethod(CACHE_KEY.format(domain='{url.netloc}'),
                  cachename=DEFAULT_CACHE_NAME)
    def origin_found_in_model(self, url):
        return super().origin_found_in_model(url)
