from django import template

from ..utils import get_ordered_user_queryset

register = template.Library()


@register.simple_tag
def ordered_users():
    """Expose the ordered user queryset to templates."""

    return get_ordered_user_queryset()