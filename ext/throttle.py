from rest_framework.throttling import SimpleRateThrottle
from django.core.cache import cache as default_cache

class MyThrottle(SimpleRateThrottle):
    scope = "xxx"
    THROTTLE_RATES = {"xxx": "5/m"}
    cache = default_cache
    def get_cache_key(self, request, view):
        if request.user:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}
