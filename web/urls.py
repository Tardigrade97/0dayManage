from django.urls import path, re_path
from web.views import account, home

urlpatterns = [
    re_path(r'^register/$', account.register, name='register'),
    re_path(r'^send/sms/$', account.send_sms, name='send_sms'),
    re_path(r'^login/sms/$', account.login_sms, name='login_sms'),
    re_path(r'^login/$', account.login, name='login'),
    re_path(r'^image/code/$', account.image_code, name='image_code'),
    re_path(r'^index/$', home.index, name='home'),
    re_path(r'^logout/$', account.logout, name='logout')

]
