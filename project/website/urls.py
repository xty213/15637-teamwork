from django.conf.urls import patterns, include, url
from django.contrib import admin
from market import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'login.html', 'extra_context':{'page_title':'Login'}}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^confirm_registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', views.confirm_registration, name='confirm_registration'),
    url(r'^buyer_view/$', views.buyer_view, name='buyer_view'),
    url(r'^item_detail/(?P<id>\d+)$', views.item_detail, name='item_detail'),
    url(r'^seller_view/$', views.seller_view, name='seller_view'),
    url(r'^my_account/$', views.my_account, name='my_account'),
    url(r'^post_item/$', views.post_item, name='post_item'),
)
