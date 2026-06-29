# Customizing Templates

DjangoForge uses Django's standard template engine with a custom design system. This guide explains how to customize the look and feel without breaking existing templates.

---

## Template structure

```
templates/
├── base.html                    # Root layout — sidebar, navbar, dark mode
├── components/
│   ├── _sidebar.html            # Left navigation sidebar
│   ├── _navbar.html             # Mobile top bar
│   ├── _flash_messages.html     # Toast notifications
│   ├── _empty_state.html        # Empty list placeholder
│   ├── _pagination.html         # Page navigation
│   └── _loading_spinner.html    # Loading indicator
├── accounts/                    # Auth pages (login, signup, profile)
├── organizations/               # Org management pages
├── billing/                     # Pricing, success, email templates
├── dashboard/                   # Main dashboard
├── errors/                      # 404, 403, 500 pages
└── emails/                      # Transactional email templates
    ├── verify_email.html
    ├── invitation.html
    ├── payment_receipt.html
    ├── payment_failed.html
    ├── subscription_cancelled.html
    └── trial_ending.html
```

---

## Design system

The design system is defined in `templates/base.html` as a `<style>` block. CSS utility classes are available throughout all templates.

### Colors

| Token | Value | Usage |
|-------|-------|-------|
| `primary-600` | Violet `#7C3AED` | Primary actions, active states |
| `primary-100` | Violet `#EDE9FE` | Icon backgrounds, hover states |
| `slate-900` | `#0F172A` | Page text (dark on light) |
| `slate-600` | `#475569` | Secondary text |
| `slate-100` | `#F1F5F9` | Surface backgrounds |

### Semantic CSS classes

These are defined in `base.html`'s `<style>` block and available everywhere:

| Class | Description |
|-------|-------------|
| `.btn-primary` | Violet filled button |
| `.btn-secondary` | Gray outlined button |
| `.btn-danger` | Red button for destructive actions |
| `.card` | White/dark card with shadow and border-radius |
| `.form-input` | Styled text input |
| `.badge` | Inline colored badge |
| `.badge-violet` | Violet badge |
| `.badge-green` | Green badge |
| `.badge-red` | Red badge |
| `.badge-amber` | Amber badge |
| `.badge-gray` | Gray badge |
| `.nav-item` | Sidebar navigation link |
| `.nav-item.active` | Active sidebar link (violet fill) |

### Typography scale

| Class | Size | Weight | Usage |
|-------|------|--------|-------|
| `text-2xl font-bold` | 24px 700 | Page headings |
| `text-lg font-semibold` | 18px 600 | Section headings |
| `text-sm font-medium` | 14px 500 | Labels, nav items |
| `text-sm` | 14px 400 | Body text |
| `text-xs` | 12px 400 | Metadata, timestamps |

---

## Template inheritance

All pages extend `base.html`:

```html
{% extends "base.html" %}
{% block title %}My Page — DjangoForge{% endblock %}

{% block content %}
  <!-- Your page content -->
{% endblock %}
```

Available blocks:

| Block | Description |
|-------|-------------|
| `title` | `<title>` tag content |
| `content` | Main page area (inside `<main>`) |
| `extra_head` | Additional `<link>` or `<meta>` tags in `<head>` |
| `extra_scripts` | Additional `<script>` tags before `</body>` |

---

## Hiding the sidebar

For full-screen pages (login, create org), hide the sidebar:

```html
{% extends "base.html" %}
{% block content %}
{% with hide_sidebar=True %}
  <div class="min-h-screen flex items-center justify-center">
    <!-- full-screen content -->
  </div>
{% endwith %}
{% endblock %}
```

---

## Using components

### Flash messages

Flash messages are automatic — `_flash_messages.html` is included in `base.html`. Trigger them in views:

```python
from django.contrib import messages
messages.success(request, "Settings saved.")
messages.error(request, "Something went wrong.")
messages.warning(request, "Your trial ends in 3 days.")
```

### Empty state

```html
{% include "components/_empty_state.html" with
    title="No reports yet"
    message="Create your first report to get started."
    action_url="/reports/create/"
    action_label="New Report"
%}
```

### Pagination

```html
{% include "components/_pagination.html" with page_obj=page_obj %}
```

---

## Custom template filters

Load the `df_filters` library in any template that needs them:

```html
{% load df_filters %}

{{ event.action|humanize_action }}  {# "billing.plan_changed" → "Billing Plan Changed" #}
{{ request.user|initials }}         {# "Ada Lovelace" → "AL" #}
```

Adding a new filter in `apps/accounts/templatetags/df_filters.py`:

```python
@register.filter
def truncate_words_middle(value, arg):
    """Truncate a string in the middle: 'A very long string' → 'A ver...ring'"""
    length = int(arg)
    if len(value) <= length:
        return value
    half = length // 2
    return f"{value[:half]}...{value[-half:]}"
```

---

## Dark mode

Dark mode is toggled by Alpine.js and persisted in `localStorage` key `df-dark`.

Add dark-mode variants to any element using Tailwind's `dark:` prefix:

```html
<div class="bg-white dark:bg-slate-900 text-slate-900 dark:text-white">
  Content
</div>
```

The `dark` class is applied to the `<html>` element by Alpine.js at page load:

```javascript
// In base.html
document.documentElement.classList.toggle('dark', localStorage.getItem('df-dark') === '1')
```

---

## Changing the brand color

To change from violet to a different color, update the Tailwind config in `base.html`:

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",   // blue-50
          100: "#dbeafe",  // blue-100
          // ... full scale
          600: "#2563eb",  // blue-600 (was #7C3AED violet)
          700: "#1d4ed8",  // blue-700
          // ...
        }
      }
    }
  }
}
```

Then update the CSS class `.btn-primary` in the `<style>` block to use `blue-600`.

---

## Changing the logo

Replace the logo SVG/text in `templates/components/_sidebar.html`:

```html
<!-- Logo section — around line 5 -->
<div class="flex items-center gap-2 px-4 py-5 border-b border-slate-100 dark:border-slate-800">
  <!-- Replace this with your logo -->
  <img src="{% static 'images/logo.svg' %}" alt="MyApp" class="h-8 w-8">
  <span class="font-bold text-slate-900 dark:text-white text-lg">MyApp</span>
</div>
```

---

## Email templates

Email templates use table-based HTML with inline CSS for email client compatibility. They do not use Tailwind classes.

All email templates share:
- Max-width 520px container
- 4px gradient accent bar at the top (change the gradient for your brand color)
- DjangoForge logo block (replace with your logo)
- Footer with copyright

To change the brand color in emails, update the accent bar gradient in each template:

```html
<!-- Find this in each email template and update the colors -->
<td style="background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%); height: 4px;"></td>
```
