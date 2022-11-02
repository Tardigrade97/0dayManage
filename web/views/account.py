from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterModelForm, SendSmsForm
from django.http import JsonResponse
from web import models


def register(request):
    """ 注册 """
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, "register.html", {'form': form})
    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        # 验证数据通过,写入数据库
        # models.UserInfo.objects.create(**data)
        # 作用如上,并且还可剔除如多余的字段数据
        form.save()
        return JsonResponse({'status': True, 'data': '/login/'})
    return JsonResponse({'status': False, 'error': form.errors})


def send_sms(request):
    # 发送短信
    sform = SendSmsForm(request, data=request.GET)
    # 校验手机号：不能为空 、格式是否正确
    if sform.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': sform.errors})
