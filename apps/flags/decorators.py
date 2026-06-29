from functools import wraps

from django.core.exceptions import PermissionDenied

from apps.flags.models import Flag


def flag_required(flag_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not flag_enabled(flag_name, request):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def flag_enabled(flag_name, request):
    try:
        flag = Flag.objects.get(name=flag_name)
        org = getattr(request, "org", None)
        return flag.is_enabled_for(request.user, org=org)
    except Flag.DoesNotExist:
        return False
