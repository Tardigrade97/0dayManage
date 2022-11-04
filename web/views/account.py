from django.shortcuts import render, HttpResponse, redirect
from web.forms.account import RegisterModelForm, SendSmsForm, LoginSMSForm, LoginForm
from django.http import JsonResponse
from utils.code import generate_code
from web import models
from io import BytesIO


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


def login_sms(request):
    if request.method == 'GET':
        form = LoginSMSForm()
        return render(request, 'login_sms.html', {'form': form})

    form = LoginSMSForm(request.POST)
    if form.is_valid():
        user_object = form.cleaned_data['mobil_phone']

        # print(user_object)
        # TODO: 用户信息放入Session
        request.session['user_id'] = user_object.id
        request.session.set_expiry(60 * 60)
        # 返回 重定向uri 和 成功状态到前端
        return JsonResponse({'status': True, 'data': "/index/"})
    return JsonResponse({'status': False, 'error': form.errors})


def login(request):
    if request.method == 'GET':
        form = LoginForm(request)
        return render(request, 'login_code.html', {'form': form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        # user_object = models.UserInfo.objects.filter(username=username, password=password).first()
        from django.db.models import Q
        user_object = models.UserInfo.objects.filter(Q(email=username) | Q(mobil_phone=username)).filter(
            password=password).first()

        # 登录成功
        if user_object:
            request.session['user_id'] = user_object.id
            request.session.set_expiry(60 * 60)
            return redirect('/index/')
        form.add_error('username', '用户名或密码错误')
    return render(request, 'login_code.html', {'form': form})


def image_code(request):
    image_object, code = generate_code.check_code()

    request.session['image_code'] = code
    # 设置session的过期时间
    request.session.set_expiry(60)
    # 图片写入到内存中
    stream = BytesIO()
    image_object.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    # 清空session
    request.session.flush()
    return redirect('/index/')
