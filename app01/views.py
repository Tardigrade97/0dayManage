import random

from django.shortcuts import render, HttpResponse
from utils.tencent.sms import send_sms_single
from django.conf import settings


# Create your views here.
def send_sms(request):
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLAT.get(tpl)
    if not template_id:
        return HttpResponse('模板不存在')

    code = random.randrange(1000, 9999)
    res = send_sms_single('18209620368', template_id, [code, ])
    if res['result'] == 0:
        return HttpResponse('成功')
    return HttpResponse(res['errmsg'])
