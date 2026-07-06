from django.db import models


class S6000Config(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    value = models.TextField(verbose_name='配置值')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 's6000_config'
        verbose_name = 'S6000 配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.key
