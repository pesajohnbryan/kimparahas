from django import template
from django.utils.timesince import timesince
from django.utils.timezone import is_naive, make_aware, now
from datetime import datetime

register = template.Library()

@register.filter
def time_ago_in_units(value):
    """
    Converts a datetime to a relative time string like '5m' or '2h'.
    Handles timezone-aware and naive datetimes.
    """
    if not value:
        return ""

    # Convert naive datetime to aware if USE_TZ = True
    if is_naive(value):
        value = make_aware(value)

    # Calculate the time difference
    time_diff = timesince(value, now())
    if "minute" in time_diff:
        return f"{time_diff.split()[0]}m"
    elif "hour" in time_diff:
        return f"{time_diff.split()[0]}h"
    return "now"

@register.filter
def user_liked_post(post, user):
    return user in post.likes.all()