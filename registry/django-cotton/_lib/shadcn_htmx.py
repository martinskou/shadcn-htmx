"""Server-side calculations for the Django-Cotton flavour.

Register with TEMPLATES[...]['OPTIONS']['libraries']:
    {'shadcn_htmx': 'shadcn_htmx'}

Tags return data, never marked-safe HTML. Templates retain Django autoescaping.
"""
import math
import re

from django import template

register = template.Library()


def _number(value, default=0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


@register.simple_tag
def scn_clamp(value, minimum=0, maximum=100):
    minimum = _number(minimum)
    maximum = max(minimum, _number(maximum, 100))
    return min(maximum, max(minimum, _number(value, minimum)))


@register.simple_tag
def scn_progress(value, minimum=0, maximum=100):
    minimum = _number(minimum)
    maximum = _number(maximum, 100)
    current = scn_clamp(value, minimum, maximum)
    percent = (current - minimum) / (maximum - minimum) * 100 if maximum > minimum else 0
    return {'value': current, 'percent': percent}


@register.simple_tag
def scn_range(low, high, minimum=0, maximum=100):
    low = scn_clamp(minimum if low is None else low, minimum, maximum)
    high = max(low, scn_clamp(maximum if high is None else high, minimum, maximum))
    return {
        'low': low,
        'high': high,
        'low_percent': scn_progress(low, minimum, maximum)['percent'],
        'high_percent': scn_progress(high, minimum, maximum)['percent'],
    }


@register.simple_tag
def scn_stars(maximum=5):
    return range(max(1, int(_number(maximum, 5))), 0, -1)


@register.simple_tag
def scn_split_matches(text, query='', words=False, case_sensitive=False):
    """Preserve source casing and escape query terms before regex matching."""
    text = str(text or '')
    query = str(query or '').strip()
    if not query:
        return [{'text': text, 'match': False}]
    terms = query.split() if words else [query]
    pattern = '|'.join(re.escape(term) for term in terms)
    flags = 0 if case_sensitive else re.IGNORECASE
    segments = []
    end = 0
    for match in re.finditer(pattern, text, flags):
        if match.start() > end:
            segments.append({'text': text[end:match.start()], 'match': False})
        segments.append({'text': match.group(), 'match': True})
        end = match.end()
    if end < len(text):
        segments.append({'text': text[end:], 'match': False})
    return segments
