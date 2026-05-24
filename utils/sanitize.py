import bleach

ALLOWED_TAGS  = []
ALLOWED_ATTRS = {}

def clean(value):
    """Strip all HTML and dangerous content from user input."""
    if not value:
        return ''
    return bleach.clean(
        str(value),
        tags       = ALLOWED_TAGS,
        attributes = ALLOWED_ATTRS,
        strip      = True
    ).strip()

def clean_form(form_data, fields):
    """Clean multiple fields at once from a form."""
    return {f: clean(form_data.get(f, '')) for f in fields}