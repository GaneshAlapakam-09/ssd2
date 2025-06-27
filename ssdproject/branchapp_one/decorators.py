from django.http import HttpResponseForbidden

def branch_one_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.Office_Branch == 'branch_one':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access restricted to branch_one users only.")
    return _wrapped_view
