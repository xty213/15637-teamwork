from django.conf.urls import patterns, include, url
from django.contrib import admin
from market import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home, name='home'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'login.html', 'extra_context':{'page_title':'Login'}}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^confirm_registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', views.confirm_registration, name='confirm_registration'),
    url(r'^send_verification_email/$', views.send_verification_email, name='send_verification_email'),
    url(r'^reset_password/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', views.reset_password, name='reset_password'),
    url(r'^buyer_view/$', views.buyer_view),
    url(r'^buyer_view/(?P<id>\d+)$', views.buyer_view, name='buyer_view'),
    url(r'^item_detail/(?P<id>\d+)$', views.item_detail, name='item_detail'),
    url(r'^seller_view/$', views.seller_view),
    url(r'^seller_view/(?P<id>\d+)$', views.seller_view, name='seller_view'),
    url(r'^my_account/$', views.my_account, name='my_account'),
    url(r'^post_item/$', views.post_item, name='post_item'),
    url(r'^buy_fixed_price_item/$', views.buy_fixed_price_item, name='buy_fixed_price_item'),
    url(r'^pay_by_paypal/$', views.pay_by_paypal, name='pay_by_paypal'),
    url(r'^finish_paypal_payment/(?P<id>\d+)$', views.finish_paypal_payment, name='finish_paypal_payment'),
    url(r'^ask_question/$', views.ask_question, name='ask_question'),
    url(r'^answer_question/$', views.answer_question, name='answer_question'),
    url(r'^search/$', views.search, name='search'),
    url(r'^place_bid/$', views.place_bid, name='place_bid'),
    url(r'^rate/$', views.rate, name='rate'),
    url(r'^media/item/(?P<itemid>\d+)/(?P<index>\d+)$', views.get_item_pic, name="get_item_pic"),
    url(r'^show_message/(?P<id>\d+)$', views.show_message, name='show_message'),
    url(r'^send_message/(?P<username>[a-zA-Z0-9_@\+\-]+)$', views.send_message, name='send_message'),
    url(r'^delete_message/(?P<id>\d+)$', views.delete_message, name='delete_message'),
    url(r'^post_demand/$', views.post_demand, name='post_demand'),
)
