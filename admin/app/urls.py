from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from carb import views

urlpatterns = [
    path('', views.StatusView.as_view(), name='status'),
    path('first-run/', views.FirstRunView.as_view(), name='first-run'),
    path('harbor/auth/', views.harbor_auth, name='harbor-auth'),
    path('calendar/', TemplateView.as_view(
        template_name='calendar.html', extra_context={'title': 'Custom Title'}), name='calendar'),
    path('admin/', admin.site.urls),
]
