from django.contrib import admin
from .models import QARecord

@admin.register(QARecord)
class QARecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer', 'created_at')
    search_fields = ('question', 'answer')
    list_filter = ('created_at',)
