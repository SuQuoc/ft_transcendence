from django.conf import settings
from silk.profiling.profiler import silk_profile

def conditional_silk_profile(view_func, name):
    if settings.SILK == True:
        return silk_profile(name=name)(view_func)
    return view_func
