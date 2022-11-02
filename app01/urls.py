from django.urls import path, re_path
from app01 import views

app_name = 'app01'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('send/sms/', views.send_sms),
    path('register/', views.register, name='register')  # "app01:register"
]
