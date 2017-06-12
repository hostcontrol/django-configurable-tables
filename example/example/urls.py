from django.conf.urls import patterns, include, url
from django.contrib import admin

from main.views import Main

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', Main.as_view()),
)
