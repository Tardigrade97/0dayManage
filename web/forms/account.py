import random
from django import forms
from web import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from utils.tencent.sms import send_sms_single
from django_redis import get_redis_connection
from utils.encrypt import md5

"""
    因为每个类都需要引入bootstrap，所以写入一个bootstrap的Basic类供其他类继承。
    Basic类
"""


class BootStrapForm(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
            name: 数据库的英文字段。
            field: 可以看作是forms.CharField(label='密码', widget=forms.PasswordInput())对象。
        '''
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = '请输入' + field.label


class RegisterModelForm(BootStrapForm, forms.ModelForm):
    password = forms.CharField(label='密码', min_length=8, max_length=32, error_messages={
        'min_length': "密码长度不能小于8位",
        'max_length': "密码长度不能大于32位"
    }, widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='确认密码', min_length=8, max_length=32, error_messages={
        'min_length': "确认密码长度不能小于8位",
        'max_length': "确认密码长度不能大于32位"
    }, widget=forms.PasswordInput())
    mobil_phone = forms.CharField(label='手机号',
                                  validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    # 密码限制
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    class Meta:
        model = models.UserInfo
        # 默认网页表单展示顺序
        # fields = "__all__"

        # 自定义网页表单展示顺序
        fields = ['username', 'email', 'password', 'confirm_password', 'mobil_phone', 'code']

    """
        重写构造函数，给所有的字段，添加CSS的class:'control'样式
    """

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     '''
    #         name: 数据库的英文字段。
    #         field: 可以看作是forms.CharField(label='密码', widget=forms.PasswordInput())对象。
    #     '''
    #     for name, field in self.fields.items():
    #         field.widget.attrs['class'] = 'form-control'
    #         field.widget.attrs['placeholder'] = '请输入' + field.label

    def clean_username(self):
        username = self.cleaned_data['username']
        exists = models.UserInfo.objects.filter(username=username).exists()
        if exists:
            raise ValidationError('用户已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(username=email).exists()
        if exists:
            raise ValidationError('邮箱已存在')
        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data['password']
        confirm_pwd = md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError('密码不一致')
        return confirm_pwd

    def clean_mobil_phone(self):
        mobil_phone = self.cleaned_data['mobil_phone']
        exists = models.UserInfo.objects.filter(username=mobil_phone).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return mobil_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        # mobil_phone = self.cleaned_data['mobil_phone']
        mobil_phone = self.cleaned_data.get('mobil_phone')
        if not mobil_phone:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(mobil_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送.')
        if redis_code.decode('utf-8') != code.strip():
            raise ValidationError('验证码错误.')


class SendSmsForm(forms.Form):
    mobil_phone = forms.CharField(label='手机号',
                                  validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobil_phone(self):
        mobil_phone = self.cleaned_data['mobil_phone']
        # 判断短信模板是否有问题
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('短信模板错误')
        exists = models.UserInfo.objects.filter(mobil_phone=mobil_phone).exists()

        if tpl == 'login':
            if not exists:
                raise ValidationError('手机号不存在')
        else:
            # 校验数据库中是否已有手机号
            if exists:
                raise ValidationError('手机号已存在')

        # 发送短信
        code = random.randrange(1000, 9999)

        sms = send_sms_single(mobil_phone, template_id, [code, ])
        if sms['result'] != 0:
            raise ValidationError('短信发送失败,{}'.format(sms['errmsg']))

        # 验证码写入redis
        conn = get_redis_connection()
        conn.set(mobil_phone, code, ex=60)
        return mobil_phone


class LoginSMSForm(BootStrapForm, forms.Form):
    mobil_phone = forms.CharField(label='手机号',
                                  validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
    # 密码限制
    code = forms.CharField(label='验证码', widget=forms.TextInput())

    """
        校验前端POST传入数据
    """

    def clean_mobil_phone(self):
        mobil_phone = self.cleaned_data['mobil_phone']
        # exists = models.UserInfo.objects.filter(mobil_phone=mobil_phone).exists()

        # 返回的是用户对象：可以类比为一个结构体
        user_object = models.UserInfo.objects.filter(mobil_phone=mobil_phone).first()
        if not user_object:
            raise ValidationError('手机号不存在')
        return user_object

    def clean_code(self):
        code = self.cleaned_data['code']
        user_object = self.cleaned_data.get('mobil_phone')
        if not user_object:
            return code
        conn = get_redis_connection()
        # redis_code 取出来是字节，需要转换为string
        redis_code = conn.get(user_object.mobil_phone)
        if not redis_code:
            raise ValidationError('验证码失效或未发送')
        if code.strip() != redis_code.decode('utf-8'):
            raise ValidationError('验证码错误')
        return code


class LoginForm(BootStrapForm, forms.Form):
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(label='密码', widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='图片验证码')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        pwd = self.cleaned_data['password']
        return md5(pwd)

    def clean_code(self):
        """校验图片验证码"""
        code = self.cleaned_data['code']
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('验证码已过期')
        if code.strip().upper() != session_code.upper():
            raise ValidationError('验证码错误')
        return code
