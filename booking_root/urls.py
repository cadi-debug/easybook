from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import TemplateView
from contact.views import about

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls', namespace='accounts')),
    path('hotels/', include('hotel.urls', namespace='hotel')),
    path('cars/', include('cars.urls', namespace='cars')),
    path('flight/', include('fly.urls', namespace='fly')),
    path('contact/', include('contact.urls', namespace='contact')),
    path('about/', about, name='about'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)