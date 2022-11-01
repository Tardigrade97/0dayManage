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


from django import forms
from app01 import models
from django.core.validators import RegexValidator


class RegisterModelForm(forms.ModelForm):
    mobil_phone = forms.CharField(label='手机号', validators=[RegexValidator(
        r'/^(?:(?:\+|00)86)?1(?:(?:3[\d])|(?:4[5-79])|(?:5[0-35-9])|(?:6[5-7])|(?:7[0-8])|(?:8[\d])|(?:9[189]))\d{8}$/',
        '手机号格式错误'), ])
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput())
    code = forms.CharField(label='验证码')

    class Meta:
        model = models.UserInfo
        # 默认网页表单展示顺序
        # fields = "__all__"

        # 自定义网页表单展示顺序
        fields = ['username', 'email', 'password', 'confirm_password', 'mobil_phone', 'code']

    """
        重写构造函数，给所有的字段，添加CSS的class:'control'样式
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
            name: 数据库的英文字段。
            field: 可以看作是forms.CharField(label='密码', widget=forms.PasswordInput())对象。
        '''
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入' + field.label


def register(request):
    form = RegisterModelForm()
    return render(request, "register.html", {'form': form})
