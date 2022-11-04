from django.utils.deprecation import MiddlewareMixin
from web import models


class auth_middleware(MiddlewareMixin):
    def process_request(self, request):
        # 如果用户已经登陆，则request中赋值
        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(id=user_id).first()
        request.tracer = user_object
