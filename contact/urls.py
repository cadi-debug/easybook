from django.urls import path
from .views import contact_view, about

app_name = 'contact'

urlpatterns = [
    path('contact/', contact_view, name='contact'),
]