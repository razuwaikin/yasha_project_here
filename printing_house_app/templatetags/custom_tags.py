from django import template
from ..views import has_role

register = template.Library()

@register.filter
def has_role_filter(user, role):
    return has_role(user, role)