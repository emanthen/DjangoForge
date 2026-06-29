from apps.flags.models import Flag


class FlagProxy:
    def __init__(self, request):
        self._request = request
        self._cache = {}

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in self._cache:
            try:
                flag = Flag.objects.get(name=name)
                org = getattr(self._request, "org", None)
                self._cache[name] = flag.is_enabled_for(self._request.user, org=org)
            except Flag.DoesNotExist:
                self._cache[name] = False
        return self._cache[name]


def flags(request):
    return {"flags": FlagProxy(request)}
