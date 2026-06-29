from django.db import models

# Create your models here.


class Depart(models.Model):
    title = models.CharField(verbose_name="部门", max_length=32)
    order = models.IntegerField(verbose_name="顺序")
    count = models.IntegerField(verbose_name="人数")


class UserInfo(models.Model):
    name = models.CharField(verbose_name="姓名", max_length=32)
    age = models.IntegerField(verbose_name="年龄")
    gender = models.SmallIntegerField(verbose_name="性别", choices=((1, "男"), (2, "女")))
    depart = models.ForeignKey(verbose_name="部门", to="Depart", on_delete=models.CASCADE)
    ctime = models.DateTimeField(verbose_name="时间", auto_now_add=True)
