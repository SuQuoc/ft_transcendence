from django.conf import settings

def conditional_silk_profile(view_func, name):
    if settings.SILK == True:
        from silk.profiling.profiler import silk_profile
        return silk_profile(name=name)(view_func)
    return view_func
