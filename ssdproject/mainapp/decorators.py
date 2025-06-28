from django.http import HttpResponseForbidden

def admin_branch_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.Office_Branch == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access restricted to admin branch users only.")
    return _wrapped_view
