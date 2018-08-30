from corsheaders.middleware import CorsMiddleware

from pik.core.cache import cachedmethod


class CachedCorsMiddleware(CorsMiddleware):
    @cachedmethod("cors_{url.netloc}")
    def origin_found_in_model(self, url):
        return super().origin_found_in_model(url)
