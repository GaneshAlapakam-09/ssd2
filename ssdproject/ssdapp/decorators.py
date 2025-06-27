from django.http import HttpResponseForbidden

def main_branch_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.Office_Branch == 'main':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access restricted to main branch users only.")
    return _wrapped_view
