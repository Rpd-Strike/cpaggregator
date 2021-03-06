"""cpaggregator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.urls import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView

from . import views, settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('info.urls')),
    path('', views.HomeView.as_view(), name='home'),
    path('', include('contact.urls')),
    path('ladders/', include(('ladders.urls', 'ladders'), namespace='ladders')),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),
    path('markdownx/', include('markdownx.urls')),
    url(r'^favicon.ico$',
        RedirectView.as_view(url=staticfiles_storage.url('favicon.ico')),
        name="favicon"
    ),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]