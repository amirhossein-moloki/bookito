from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# پیکربندی Swagger و Redoc
schema_view = get_schema_view(
    openapi.Info(
        title="Book Store API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@bookstore.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # دسترسی عمومی
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # URLs مربوط به اپلیکیشن‌ها
    path('accounts/', include('accounts.urls')),
    path('authors/', include('authors.urls')),
    path('books/', include('books.urls')),
    path('customers/', include('customers.urls')),

    path('discounts/', include('discounts.urls')),
    path('genres/', include('genres.urls')),
    path('language/', include('Language.urls')),  # اصلاح نام به 'language' (با حروف کوچک)
    path('publishers/', include('publishers.urls')),

    path('translators/', include('translators.urls')),
    path('address/', include('address.urls')),
    path('recommendations/', include('recommendations.urls')),

    # URL برای نمایش Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # URL برای نمایش Redoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-ui'),
]

# اضافه کردن پیکربندی برای نمایش فایل‌های مدیا
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
