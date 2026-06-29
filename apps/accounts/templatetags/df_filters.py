from django import template

register = template.Library()


@register.filter
def split(value, delimiter=","):
    return str(value).split(delimiter)


@register.filter
def humanize_action(value):
    """Convert 'user.email_verified' → 'User Email Verified'"""
    return str(value).replace("_", " ").replace(".", " ").title()


@register.filter
def initials(user):
    if not user:
        return "?"
    fn = getattr(user, "first_name", "") or ""
    ln = getattr(user, "last_name", "") or ""
    if fn and ln:
        return f"{fn[0]}{ln[0]}".upper()
    email = getattr(user, "email", "") or ""
    return email[0].upper() if email else "?"
