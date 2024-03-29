from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from . import settings
from .views import page_404

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description"
    ),
    public=True,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('app.urls')),
    path('api/v1/', include('backoffice.api.urls')),
    path('payments/', include('payments.urls')),
    path('graph', include('mptt_graph.urls')),
    path('page_404', page_404, name='page_404'),
    path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += i18n_patterns(
    path('backoffice/', include('backoffice.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_title = "HR"
admin.site.site_header = "Algorithm-Getaway HR"
admin.site.index_title = "Algorithm-Getaway HRga hush kelibsiz"

# handler404 = 'backoffice.views.page_404'
