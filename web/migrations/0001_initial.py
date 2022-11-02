# Generated by Django 4.1.2 on 2022-11-01 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=16, verbose_name='用户名')),
                ('email', models.EmailField(max_length=32, verbose_name='邮箱')),
                ('mobil_phone', models.CharField(max_length=32, verbose_name='手机号码')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
            ],
        ),
    ]
