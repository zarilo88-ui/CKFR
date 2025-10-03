import logging

from django import template
from django.urls import Resolver404, resolve

from ..utils import get_ordered_user_queryset

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def ordered_users():
    """Expose the ordered user queryset to templates."""

    return get_ordered_user_queryset()


@register.simple_tag(takes_context=True)
def current_url_name(context):
    """Return the resolved URL name for the current request.

    Some runtime contexts (notably the CSRF failure view) render templates
    without attaching ``resolver_match`` to the request.  Accessing
    ``request.resolver_match`` in templates would then raise an ``AttributeError``
    and blow up the response.  We resolve the path manually in those rare cases
    and default to an empty string when resolution fails so callers can perform
    defensive comparisons.
    """

    request = context.get("request")
    if request is None:
        return ""

    match = getattr(request, "resolver_match", None)
    if match is None:
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return ""
        except Exception:  # pragma: no cover - defensive safety net
            logger.exception("Failed to resolve URL for path %s", getattr(request, "path_info", "<unknown>"))
            return ""

    return match.url_name or ""
