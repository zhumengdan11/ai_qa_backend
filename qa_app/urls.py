from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/chat', views.chat_api, name='chat_api'),
    path('api/chat/list', views.chat_list, name='chat_list'),
    path('api/chat/delete', views.chat_delete, name='chat_delete'),
    path('api/chat/batch-clear', views.chat_batch_clear, name='chat_batch_clear'),
    path('api/chat/export', views.chat_export, name='chat_export'),
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('api/admin/login', views.admin_login_api, name='admin_login_api'),
    path('api/admin/check', views.admin_check, name='admin_check'),
    path('api/admin/logout', views.admin_logout, name='admin_logout'),
]
