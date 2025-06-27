def branch_url_context(request):
    path = request.path
    if path.startswith('/main/'):
        return {'branch_url': 'ssdapp'}
    elif path.startswith('/branch_one/'):
        return {'branch_url': 'branchapp_one'}
    return {'branch_url': 'ssdapp'}  # default fallback
