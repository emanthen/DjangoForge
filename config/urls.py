from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "DjangoForge Admin"
admin.site.site_title = "DjangoForge"
admin.site.index_title = "Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("", include("apps.organizations.urls")),
    path("billing/", include("apps.billing.urls")),
    path("api/", include("apps.api.urls")),
    path("accounts/", include("allauth.urls")),
    path("hijack/", include("hijack.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "apps.api.views.handler404"
handler500 = "apps.api.views.handler500"
handler403 = "apps.api.views.handler403"

# Redirect root to dashboard or login
from django.views.generic import RedirectView
urlpatterns += [
    path("", RedirectView.as_view(pattern_name="accounts:dashboard"), name="home"),
]
