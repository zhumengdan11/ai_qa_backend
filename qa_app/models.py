from django.db import models
from django.utils import timezone

class QARecord(models.Model):
    """问答记录模型"""
    question = models.TextField(verbose_name='用户问题')
    answer = models.TextField(verbose_name='AI回答', blank=True)
    created_at = models.DateTimeField(verbose_name='提问时间', default=timezone.now)

    class Meta:
        verbose_name = '问答记录'
        verbose_name_plural = '问答记录'
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:50]
