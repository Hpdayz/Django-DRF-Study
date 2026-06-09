from django.db import models


class ThreatBookConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    value = models.TextField(verbose_name='配置值')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'threatbook_config'
        verbose_name = '微步配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.key


class ThreatBookCache(models.Model):
    resource = models.CharField(max_length=45, verbose_name='IP 地址')
    lang = models.CharField(max_length=10, default='zh', verbose_name='语言')
    response_data = models.TextField(verbose_name='响应 JSON')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'threatbook_cache'
        verbose_name = 'IP 信誉缓存'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['resource', 'lang']),
        ]

    def __str__(self):
        return f'{self.resource} ({self.lang})'
