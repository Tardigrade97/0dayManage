from django.urls import path,re_path
from web.views import account

urlpatterns = [
    re_path(r'^register/$', account.register,name='register'),
    re_path(r'^send/sms/$',account.send_sms,name='send_sms')
]
