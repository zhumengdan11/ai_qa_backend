import json
import re
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import models as db_models
import requests

from .models import QARecord


def call_qwen3_api(question):
    """调用校内 Qwen3 大模型 API"""
    api_key = settings.QWEN3_API_KEY
    base_url = settings.QWEN3_BASE_URL.rstrip("/")  # 去除末尾斜杠，防止双斜杠404
    model = settings.QWEN3_MODEL

    if not api_key:
        return '⚠️ 系统提示：API 密钥未配置，请联系管理员设置 QWEN3_API_KEY 环境变量。'

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        payload = {
            'model': model,
            'messages': [{'role': 'user', 'content': question}],
            'temperature': 0.7,
            'max_tokens': 2000
        }

        chat_url = f'{base_url}/chat/completions'
        response = requests.post(
            chat_url,
            headers=headers,
            json=payload,
            timeout=60,
            verify=False,
            proxies={"https": None, "http": None}
        )
        response.encoding = "utf‑8"

        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            # 过滤\u2011等特殊Unicode字符，解决ASCII编码报错
            content = content.replace("\u2011", "-")
            content = re.sub(r'[^\u0000-\u007f\u4e00-\u9fff]', '', content)
            return content
        elif response.status_code == 401:
            return "⚠️ API‑Key密钥错误，请核对密钥！"
        elif response.status_code == 404:
            return f"⚠️ 404错误：模型名称「{model}」不存在，请核对vLLM模型名称！"
        else:
            return f'⚠️ API请求失败 (HTTP {response.status_code}): {response.text}'

    except requests.exceptions.Timeout:
        return '⚠️ 请求超时，校园网网络波动，请重试。'
    except requests.exceptions.ConnectionError:
        return '⚠️ 无法连接AI服务，请确认已连接校园网。'
    except Exception as e:
        return f'⚠️ 请求异常: {str(e)}'


@ensure_csrf_cookie
def chat_view(request):
    """渲染问答页面"""
    return render(request, 'qa_app/chat.html')


@csrf_exempt
@require_http_methods(['POST'])
def chat_api(request):
    """处理用户提问 - 调用AI接口并保存记录"""
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()

        if not question:
            return JsonResponse({'success': False, 'message': '请输入问题'}, status=400)
        if len(question) > 2000:
            return JsonResponse({'success': False, 'message': '问题长度不能超过2000字'}, status=400)

        answer = call_qwen3_api(question)
        record = QARecord.objects.create(question=question, answer=answer)

        return JsonResponse({
            'success': True,
            'data': {
                'id': record.id,
                'question': record.question,
                'answer': record.answer,
                'created_at': record.created_at.strftime('%Y‑%m‑%d %H:%M:%S')
            }
        }, json_dumps_params={"ensure_ascii": False})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'服务器内部错误: {str(e)}'}, status=500)


def chat_list(request):
    """获取问答记录列表（支持分页和搜索）"""
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    keyword = request.GET.get('keyword', '').strip()

    records = QARecord.objects.all()
    if keyword:
        records = records.filter(
            db_models.Q(question__icontains=keyword) |
            db_models.Q(answer__icontains=keyword)
        )

    total = records.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    start = (page - 1) * page_size
    end = start + page_size
    page_records = records[start:end]

    data = [{
        'id': r.id,
        'question': r.question,
        'answer': r.answer,
        'created_at': r.created_at.strftime('%Y‑%m‑%d %H:%M:%S')
    } for r in page_records]

    return JsonResponse({
        'success': True,
        'data': data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages
        }
    }, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
@require_http_methods(['POST'])
def chat_delete(request):
    """删除单条问答记录"""
    try:
        data = json.loads(request.body)
        record_id = data.get('id')
        if not record_id:
            return JsonResponse({'success': False, 'message': '缺少记录ID'}, status=400)
        record = QARecord.objects.get(id=record_id)
        record.delete()
        return JsonResponse({'success': True, 'message': '删除成功'})
    except QARecord.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'删除失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def chat_batch_clear(request):
    """批量清空问答记录"""
    try:
        count = QARecord.objects.count()
        QARecord.objects.all().delete()
        return JsonResponse({'success': True, 'message': f'已清空 {count} 条记录'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'清空失败: {str(e)}'}, status=500)


def chat_export(request):
    """导出问答记录为文本文件"""
    keyword = request.GET.get('keyword', '').strip()
    records = QARecord.objects.all()
    if keyword:
        records = records.filter(
            db_models.Q(question__icontains=keyword) |
            db_models.Q(answer__icontains=keyword)
        )

    now_str = datetime.now().strftime('%Y‑%m‑%d %H:%M:%S')
    lines = []
    lines.append('=' * 60)
    lines.append('  AI 问答记录导出')
    lines.append(f'  导出时间: {now_str}')
    lines.append(f'  记录总数: {records.count()}')
    if keyword:
        lines.append(f'  关键词: "{keyword}"')
    lines.append('=' * 60)
    lines.append('')

    for idx, record in enumerate(records, 1):
        lines.append(f'【第 {idx} 条】')
        lines.append(f'提问时间: {record.created_at.strftime("%Y‑%m‑%d %H:%M:%S")}')
        lines.append(f'用户问题: {record.question}')
        lines.append('AI回答:')
        lines.append(record.answer)
        lines.append('')
        lines.append('-' * 40)
        lines.append('')

    lines.append('=' * 60)
    lines.append('  导出完毕')
    lines.append('=' * 60)

    content = '\n'.join(lines)
    response = HttpResponse(content, content_type='text/plain; charset=utf‑8')
    filename = f'qa_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    response['Content‑Disposition'] = f'attachment; filename="{filename}"'
    return response


def admin_login_view(request):
    """管理员登录页面"""
    if request.session.get('is_admin'):
        return redirect('admin_dashboard')
    return render(request, 'qa_app/login.html')


@csrf_exempt
@require_http_methods(['POST'])
def admin_login_api(request):
    """管理员登录 API"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        env_username = settings.ADMIN_USERNAME.strip()
        env_password = settings.ADMIN_PASSWORD.strip()

        if username == env_username and password == env_password:
            request.session['is_admin'] = True
            request.session['admin_username'] = username
            return JsonResponse({'success': True, 'message': '登录成功'})

        return JsonResponse({'success': False, 'message': '用户名或密码错误'}, status=401)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'登录失败: {str(e)}'}, status=500)


def admin_check(request):
    """检查管理员登录状态"""
    return JsonResponse({'is_admin': request.session.get('is_admin', False)})


def admin_logout(request):
    """管理员退出登录"""
    request.session.flush()
    return JsonResponse({'success': True, 'message': '已退出登录'})


def admin_dashboard(request):
    """管理后台首页"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')
    total_count = QARecord.objects.count()
    today_count = QARecord.objects.filter(
        created_at__date=datetime.now().date()
    ).count()
    context = {
        'total_count': total_count,
        'today_count': today_count,
        'admin_username': request.session.get('admin_username', '管理员'),
    }
    return render(request, 'qa_app/dashboard.html', context)