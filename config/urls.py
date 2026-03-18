from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('materials.urls')),
    path('api/users/', include('users.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('payment/success/', user_views.PaymentSuccessView.as_view(), name='payment-success'),
    path('payment/cancel/', user_views.PaymentCancelView.as_view(), name='payment-cancel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
