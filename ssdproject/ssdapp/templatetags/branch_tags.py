from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def branch_url(context, view_name):
    user = context['request'].user
    if user.is_authenticated:
        branch = user.office_branch
        if branch == 'main':
            return f'ssdapp:{view_name}'
        elif branch == 'branch_one':
            return f'branchapp_one:{view_name}'
        elif branch == 'admin':
            return f'mainapp:{view_name}'
    return f''  # fallback
