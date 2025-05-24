import os

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import random
import string
from datetime import datetime, timedelta
import json
import calendar

from .authentication import logger
from .models import (
    San, DatLich, ThongBao, NguoiDung, HoatDongNgoaiKhoa, HoiThoai, TinNhan, Nhom, ThanhVienNhom, LoiMoiNhom, BaiViet,
    CamXuc, BinhLuan, DKNgoaiKhoa, PendingRegistration, OTP, PollVote, PollOption
)
from .forms import ExtracurricularForm, TinNhanForm, LoginForm, RegisterForm, PostForm, GroupForm


# @login_required
# def post_article(request, ma_nhom):
#     """View for posting articles in a group"""
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except:
#         return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})
#
#     try:
#         # Get form data
#         content = request.POST.get('content', '')
#         post_type = request.POST.get('post_type', 'text')
#
#         if not content and post_type == 'text':
#             return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})
#
#         nhom = Nhom.objects.get(id=ma_nhom)
#
#         # Check if user is a member of this group
#         membership = ThanhVienNhom.objects.filter(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             trang_thai='DuocDuyet'
#         ).first()
#
#         if not membership:
#             return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})
#
#         # Create new post
#         bai_viet = BaiViet.objects.create(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             noi_dung=content,
#             thoi_gian_dang=timezone.now(),
#             trang_thai='ChoDuyet'  # Luôn đặt trạng thái là Chờ duyệt
#         )
#
#         # Store post type in the content with a special marker
#         if post_type != 'text':
#             bai_viet.noi_dung = f"[TYPE:{post_type}]\n{content}"
#             bai_viet.save()
#
#         # Handle file uploads if present
#         media_url = None
#         file_name = None
#
#         if post_type == 'image' and request.FILES.get('image'):
#             image_file = request.FILES.get('image')
#             fs = FileSystemStorage()
#             filename = fs.save(f'bai_viet/hinh_anh/{image_file.name}', image_file)
#             media_url = fs.url(filename)
#             bai_viet.noi_dung = f"{bai_viet.noi_dung}\n[IMAGE_URL:{media_url}]"
#             bai_viet.save()
#
#         elif post_type == 'video' and request.FILES.get('video'):
#             video_file = request.FILES.get('video')
#             fs = FileSystemStorage()
#             filename = fs.save(f'bai_viet/video/{video_file.name}', video_file)
#             media_url = fs.url(filename)
#             bai_viet.noi_dung = f"{bai_viet.noi_dung}\n[VIDEO_URL:{media_url}]"
#             bai_viet.save()
#
#         elif post_type == 'file' and request.FILES.get('file'):
#             file = request.FILES.get('file')
#             fs = FileSystemStorage()
#             filename = fs.save(f'bai_viet/tai_lieu/{file.name}', file)
#             media_url = fs.url(filename)
#             file_name = file.name
#             bai_viet.noi_dung = f"{bai_viet.noi_dung}\n[FILE_URL:{media_url}]\n[FILE_NAME:{file_name}]"
#             bai_viet.save()
#
#         elif post_type == 'poll':
#             # Process poll options
#             poll_options = []
#             option_index = 1
#
#             while request.POST.get(f'option_{option_index}'):
#                 option_text = request.POST.get(f'option_{option_index}')
#                 if option_text.strip():
#                     poll_options.append({
#                         'id': option_index,
#                         'text': option_text.strip(),
#                         'votes': 0,
#                         'voted': False
#                     })
#                 option_index += 1
#
#             if len(poll_options) >= 2:
#                 # Create poll data structure
#                 poll_data = {
#                     'id': bai_viet.id,
#                     'question': content,
#                     'options': poll_options,
#                     'total_votes': 0
#                 }
#
#                 # Add poll data to post content
#                 poll_json = json.dumps(poll_data)
#                 bai_viet.noi_dung = f"[TYPE:poll]\n{content}\n[POLL]{poll_json}[/POLL]"
#                 bai_viet.save()
#
#         # Prepare response data
#         response_data = {
#             'success': True,
#             'post_id': bai_viet.id,
#             'ho_ten': nguoi_dung.ho_ten,
#             'thoi_gian_dang': bai_viet.thoi_gian_dang.strftime('%d/%m/%Y %H:%M'),
#             'type': post_type,
#             'content': content,
#             'media_url': media_url,
#             'file_name': file_name,
#             'trang_thai': 'Chờ duyệt'  # Cập nhật thông báo
#         }
#
#         return JsonResponse(response_data)
#
#     except Nhom.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.files.storage import FileSystemStorage, default_storage
import json

# from .models import Nhom, NguoiDung, BaiViet, PollOption

@login_required
def post_article(request, ma_nhom):
    """View for posting articles in a group"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})

    try:
        nguoi_dung = request.user.nguoidung
    except:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})

    try:
        # Get form data
        content = request.POST.get('noi_dung', '').strip()
        post_type = request.POST.get('post_type', 'text')

        if not content and post_type == 'text':
            return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})

        nhom = Nhom.objects.get(id=ma_nhom)

        # Determine post status based on user role
        is_admin = nguoi_dung.vai_tro == 'Admin'
        is_moderator = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        # Check if user is a member of this group (only for non-admin users)
        if not is_admin:
            membership = ThanhVienNhom.objects.filter(
                ma_nhom=nhom,
                ma_nguoi_dung=nguoi_dung,
                trang_thai='DuocDuyet'
            ).first()
            if not membership:
                return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})

        # Set post status: Admin and moderators post directly, others need approval
        trang_thai = 'DaDuyet' if is_admin or is_moderator else 'ChoDuyet'

        # Create new post
        bai_viet = BaiViet.objects.create(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            noi_dung=content,
            thoi_gian_dang=timezone.now(),
            trang_thai=trang_thai,
            post_type=post_type
        )

        # Handle file uploads if present
        media_url = None
        file_name = None

        if post_type == 'image' and request.FILES.get('image'):
            image_file = request.FILES.get('image')
            bai_viet.image = image_file
            bai_viet.save()
            media_url = bai_viet.image.url

        elif post_type == 'video' and request.FILES.get('video'):
            video_file = request.FILES.get('video')
            bai_viet.video = video_file
            bai_viet.save()
            media_url = bai_viet.video.url

        elif post_type == 'file' and request.FILES.get('file'):
            file = request.FILES.get('file')
            bai_viet.file = file
            bai_viet.save()
            media_url = bai_viet.file.url
            file_name = file.name

        elif post_type == 'poll':
            # Validate poll options
            poll_options = []
            option_index = 1

            while request.POST.get(f'option_{option_index}'):
                option_text = request.POST.get(f'option_{option_index}').strip()
                if option_text:
                    poll_options.append(option_text)
                option_index += 1

            if len(poll_options) < 2:
                bai_viet.delete()
                return JsonResponse({'success': False, 'error': 'Thăm dò phải có ít nhất 2 lựa chọn!'})

            # Create PollOption records
            for option_text in poll_options:
                PollOption.objects.create(
                    bai_viet=bai_viet,
                    text=option_text,
                    votes=0
                )

        # Prepare response data
        response_data = {
            'success': True,
            'post_id': bai_viet.id,
            'ho_ten': nguoi_dung.ho_ten,
            'thoi_gian_dang': bai_viet.thoi_gian_dang.strftime('%d/%m/%Y %H:%M'),
            'type': post_type,
            'content': content,
            'media_url': media_url,
            'file_name': file_name,
            'trang_thai': 'Đã duyệt' if trang_thai == 'DaDuyet' else 'Chờ duyệt'
        }

        return JsonResponse(response_data)

    except Nhom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import BaiViet, PollOption, PollVote


@login_required
def get_poll(request, post_id):
    try:
        post = BaiViet.objects.get(id=post_id)
        user = request.user.nguoidung if request.user.is_authenticated else None
        options = PollOption.objects.filter(ma_bai_viet=post)

        total_votes = PollVote.objects.filter(ma_bai_viet=post).count()
        # Kiểm tra xem người dùng đã vote cho từng option chưa
        options_data = []
        for opt in options:
            # Kiểm tra xem người dùng đã vote cho option này chưa
            voted = PollVote.objects.filter(
                ma_bai_viet=post,
                ma_nguoi_dung=user,
                option_id=opt.option_id
            ).exists() if user else False
            options_data.append({
                'option_id': opt.option_id,
                'option_text': opt.option_text,
                'vote_count': opt.vote_count,
                'voted': voted
            })

        return JsonResponse({
            'success': True,
            'total_votes': total_votes,
            'options': options_data
        })
    except BaiViet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@login_required
def download_file(request, file_path):
    # file_path sẽ là đường dẫn tương đối, ví dụ: "bai_viet/tai_lieu/48K14.1-Nhom07-ChuDe3-BCTD4%20(1).docx"
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if default_storage.exists(full_path):
        with default_storage.open(full_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            # Đặt header để buộc tải về
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    else:
        return HttpResponse("File không tồn tại!", status=404)# View đăng bài viết
# @login_required
# @require_POST
# def post_article(request, ma_nhom):
#     """View for posting articles in a group"""
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except:
#         return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})
#
#     try:
#         # Get form data
#         content = request.POST.get('content')
#         post_type = request.POST.get('post_type', 'text')
#
#         if not content and post_type == 'text':
#             return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})
#
#         nhom = Nhom.objects.get(id=ma_nhom)
#
#         # Check if user is a member of this group
#         membership = ThanhVienNhom.objects.filter(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             trang_thai='DuocDuyet'
#         ).first()
#
#         if not membership:
#             return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})
#
#         # Create new post
#         bai_viet = BaiViet.objects.create(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             noi_dung=content,
#             thoi_gian_dang=timezone.now(),
#             trang_thai='ChoDuyet' if nhom.trang_thai_nhom == 'RiengTu' else 'DaDuyet'
#         )
#
#         # Store post type in the content with a special marker
#         if post_type != 'text':
#             bai_viet.noi_dung = f"[TYPE:{post_type}]\n{content}"
#             bai_viet.save()
#
#         # Handle file uploads if present
#         media_url = None
#         if post_type == 'image' and request.FILES.get('image'):
#             image_file = request.FILES.get('image')
#             fs = FileSystemStorage()
#             filename = fs.save(f'bai_viet/hinh_anh/{image_file.name}', image_file)
#             media_url = fs.url(filename)
#             bai_viet.noi_dung = f"{bai_viet.noi_dung}\n[IMAGE_URL:{media_url}]"
#             bai_viet.save()
#
#         elif post_type == 'video' and request.FILES.get('video'):
#             video_file = request.FILES.get('video')
#             fs = FileSystemStorage()
#             filename = fs.save(f'bai_viet/video/{video_file.name}', video_file)
#             media_url = fs.url(filename)
#             bai_viet.noi_dung = f"{bai_viet.noi_dung}\n[VIDEO_URL:{media_url}]"
#             bai_viet.save()
#
#         elif post_type == 'file' and request.FILES.get('file'):
#             file = request.FILES.get('file')
#             fs = FileSystemStorage()
#             filename = fs.save(f'bai_viet/tai_lieu/{file.name}', file)
#             media_url = fs.url(filename)
#             bai_viet.noi_dung = f"{bai_viet.noi_dung}\n[FILE_URL:{media_url}]\n[FILE_NAME:{file.name}]"
#             bai_viet.save()
#
#         # Prepare response data
#         response_data = {
#             'success': True,
#             'post_id': bai_viet.id,
#             'ho_ten': nguoi_dung.ho_ten,
#             'thoi_gian_dang': bai_viet.thoi_gian_dang.strftime('%d/%m/%Y %H:%M'),
#             'type': post_type,
#             'content': content,
#             'media_url': media_url,
#             'trang_thai': 'Đã duyệt' if bai_viet.trang_thai == 'DaDuyet' else 'Chờ duyệt'
#         }
#
#         return JsonResponse(response_data)
#
#     except Nhom.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})

# View thích bài viết
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import BaiViet, CamXuc, NguoiDung
from django.http import HttpResponse
from django.core.files.storage import default_storage
import os


@login_required
@require_POST
def like_post(request, ma_bai_viet):
    """View for liking or unliking a post"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'}, status=401)

    try:
        nguoi_dung = request.user.nguoidung
        bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet)

        # Kiểm tra xem người dùng đã like bài viết chưa
        cam_xuc = CamXuc.objects.filter(
            ma_bai_viet=bai_viet,
            ma_nguoi_dung=nguoi_dung
        ).first()

        response_data = {
            'success': True,
            'liked': False,
            'SoLuongCamXuc': CamXuc.objects.filter(ma_bai_viet=bai_viet).count()
        }

        if cam_xuc:
            # Nếu đã like, xóa bản ghi để bỏ like
            cam_xuc.delete()
        else:
            # Nếu chưa like, tạo bản ghi mới
            CamXuc.objects.create(
                ma_bai_viet=bai_viet,
                ma_nguoi_dung=nguoi_dung
            )
            response_data['liked'] = True

        # Cập nhật số lượng like
        response_data['SoLuongCamXuc'] = CamXuc.objects.filter(ma_bai_viet=bai_viet).count()

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



# @login_required
# @require_POST
# def them_binh_luan(request, ma_bai_viet):
#     """View for commenting on posts"""
#     logger.debug(f"Received request to add comment for post ID: {ma_bai_viet} by user: {request.user.username}")
#
#     if not request.user.is_authenticated:
#         logger.warning("User not authenticated")
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=401)
#
#     noi_dung = request.POST.get('noi_dung', '').strip()
#
#     if not noi_dung:
#         logger.warning("Comment content is empty")
#         return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống!'}, status=400)
#
#     if len(noi_dung) > 1000:
#         logger.warning("Comment content too long")
#         return JsonResponse({'success': False, 'message': 'Bình luận quá dài, tối đa 1000 ký tự!'}, status=400)
#
#     try:
#         nguoi_dung = NguoiDung.objects.get(user=request.user)
#         logger.debug(f"User found: {nguoi_dung.ho_ten}")
#     except NguoiDung.DoesNotExist:
#         logger.error(f"NguoiDung does not exist for user: {request.user.username}")
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng! Vui lòng cập nhật hồ sơ.'}, status=400)
#     except Exception as e:
#         logger.error(f"Unexpected error while fetching NguoiDung: {str(e)}")
#         return JsonResponse({'success': False, 'message': f'Lỗi không xác định khi tìm người dùng: {str(e)}'}, status=500)
#
#     try:
#         bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet)
#         logger.debug(f"Post found: {bai_viet.id}")
#
#         # Kiểm tra quyền truy cập nhóm (nếu bài viết thuộc nhóm)
#         if bai_viet.ma_nhom:
#             membership = ThanhVienNhom.objects.filter(
#                 ma_nhom=bai_viet.ma_nhom,
#                 ma_nguoi_dung=nguoi_dung,
#                 trang_thai='DuocDuyet'
#             ).first()
#             if not membership:
#                 logger.warning(f"User {nguoi_dung.ho_ten} has no permission to comment on post {ma_bai_viet}")
#                 return JsonResponse({'success': False, 'message': 'Bạn không có quyền bình luận trong nhóm này!'}, status=403)
#     except Exception as e:
#         logger.error(f"Error fetching post or membership: {str(e)}")
#         return JsonResponse({'success': False, 'message': f'Không tìm thấy bài viết hoặc lỗi quyền truy cập: {str(e)}'}, status=404)
#
#     try:
#         binh_luan = BinhLuan.objects.create(
#             ma_bai_viet=bai_viet,
#             ma_nguoi_dung=nguoi_dung,
#             noi_dung=noi_dung,
#             thoi_gian=timezone.now()
#         )
#         logger.info(f"Comment created successfully: {binh_luan.id}")
#
#         # Cập nhật số lượng bình luận (cho frontend)
#         comment_count = BinhLuan.objects.filter(ma_bai_viet=bai_viet).count()
#     except Exception as e:
#         logger.error(f"Error creating comment: {str(e)}")
#         return JsonResponse({'success': False, 'message': f'Lỗi khi tạo bình luận: {str(e)}'}, status=500)
#
#     try:
#         avatar_url = nguoi_dung.avatar.url if nguoi_dung.avatar else '/static/default-avatar.png'
#         logger.debug(f"Avatar URL: {avatar_url}")
#     except Exception as e:
#         logger.error(f"Error accessing avatar: {str(e)}")
#         avatar_url = '/static/default-avatar.png'
#
#     return JsonResponse({
#         'success': True,
#         'message': 'Bình luận đã được gửi!',
#         'comment_id': binh_luan.id,
#         'ho_ten': nguoi_dung.ho_ten,
#         'noi_dung': noi_dung,
#         'time': binh_luan.thoi_gian.strftime('%d/%m/%Y %H:%M'),
#         'avatar_url': avatar_url,
#         'comment_count': comment_count  # Thêm số lượng bình luận
#     })


# View cho bảng tin nhóm
@login_required
def group_feed(request):
    if not request.user.is_authenticated:
        return render(request, 'social/Nhom/error.html', {'message': 'Người dùng chưa đăng nhập!'})

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})

    thanh_vien_nhom = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet'
    ).values_list('ma_nhom', flat=True)

    posts = BaiViet.objects.filter(
        ma_nhom__in=thanh_vien_nhom,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung', 'ma_nhom').order_by('-thoi_gian_dang')

    # Tạo danh sách bài viết với số từ
    posts_with_wordcount = []
    for post in posts:
        word_count = len(post.noi_dung.strip().split())
        posts_with_wordcount.append({
            'post': post,
            'word_count': word_count
        })

    context = {
        'posts_with_wordcount': posts_with_wordcount,
        'nguoi_dung': nguoi_dung,
    }
    return render(request, 'social/group.html', context)


# @login_required
# @require_POST
# def add_comment(request, ma_bai_viet):
#     """View for adding comments to a post"""
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=400)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'},
#                             status=400)
#
#     bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet)
#     noi_dung = request.POST.get('content')
#
#     if not noi_dung:
#         return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống!'}, status=400)
#
#     binh_luan = BinhLuan.objects.create(
#         ma_bai_viet=bai_viet,
#         ma_nguoi_dung=nguoi_dung,
#         noi_dung=noi_dung,
#         thoi_gian=timezone.now()
#     )
#
#     # Thêm thông tin người dùng để hiển thị trên frontend
#     avatar_url = nguoi_dung.avatar.url if nguoi_dung.avatar else None
#
#     return JsonResponse({
#         'success': True,
#         'message': 'Bình luận đã được gửi!',
#         'username': nguoi_dung.ho_ten,
#         'avatar_url': avatar_url,
#         'content': noi_dung,
#         'time': binh_luan.thoi_gian.strftime('%d/%m/%Y %H:%M')
#     })


@login_required
def group_list(request):
    return render(request, 'social/group.html', {'show_modal': False})
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Nhom, NguoiDung, ThanhVienNhom

import logging

# Thiết lập logging
logger = logging.getLogger(__name__)


@login_required
def tao_nhom_moi(request):
    if not request.user.is_authenticated:
        logger.error("Người dùng chưa đăng nhập khi cố gắng tạo nhóm")
        return JsonResponse({'success': False, 'error': 'Bạn cần đăng nhập để tạo nhóm!'}, status=401)

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        logger.error("Không tìm thấy thông tin người dùng")
        return JsonResponse(
            {'success': False, 'error': 'Không tìm thấy thông tin người dùng. Vui lòng cập nhật hồ sơ.'}, status=400)

    if request.method == 'POST':
        try:
            ten_nhom = request.POST.get('group_name')
            mo_ta = request.POST.get('group_description', '')
            avatar = request.FILES.get('avatar')
            cover_image = request.FILES.get('cover_image')

            if not ten_nhom:
                logger.warning("Yêu cầu tạo nhóm không có tên nhóm")
                return JsonResponse({'success': False, 'error': 'Vui lòng nhập tên nhóm!'}, status=400)

            # Log thông tin file
            logger.info(
                f"File upload - Avatar: {avatar.name if avatar else 'None'}, Cover: {cover_image.name if cover_image else 'None'}")

            # Tạo nhóm mới
            nhom = Nhom.objects.create(
                ten_nhom=ten_nhom,
                mo_ta=mo_ta,
                trang_thai='ChoDuyet',
                nguoi_tao=nguoi_dung,
                avatar=avatar,
                cover_image=cover_image
            )

            # Log đường dẫn file sau khi lưu
            logger.info(
                f"Nhóm '{ten_nhom}' được tạo với avatar: {nhom.avatar.url if nhom.avatar else 'None'}, cover_image: {nhom.cover_image.url if nhom.cover_image else 'None'}")

            # Thêm người tạo làm quản trị viên
            ThanhVienNhom.objects.create(
                ma_nhom=nhom,
                ma_nguoi_dung=nguoi_dung,
                trang_thai='DuocDuyet',
                la_quan_tri_vien=True
            )
            logger.info(f"{nguoi_dung.ho_ten} được thêm làm quản trị viên của nhóm '{ten_nhom}'")

            return JsonResponse({
                'success': True,
                'message': f'Nhóm "{ten_nhom}" đã được gửi yêu cầu tạo! Đang chờ duyệt.'
            })
        except Exception as e:
            logger.error(f"Lỗi khi tạo nhóm: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Có lỗi xảy ra: {str(e)}'}, status=500)

    # GET request: Hiển thị form tạo nhóm
    logger.info(f"Hiển thị form tạo nhóm cho {nguoi_dung.ho_ten}")
    return render(request, 'social/Nhom/tao_nhom_moi.html', {'nguoi_dung': nguoi_dung})
from django.core.paginator import Paginator
from django.db.models import Q


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Nhom, NguoiDung, ThanhVienNhom

# @login_required
# def search_groups(request):
#     if not request.user.is_authenticated:
#         return render(request, 'social/Nhom/error.html', {'message': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})
#
#     # Lấy tham số tìm kiếm từ request
#     search_query = request.GET.get('search', '').strip().lower()
#
#     # Tạo query tìm kiếm
#     query = Q(ten_nhom__icontains=search_query) | Q(mo_ta__icontains=search_query)
#     query &= Q(trang_thai='DaDuyet')  # Chỉ lấy nhóm đã được duyệt
#
#     # Lấy tất cả nhóm phù hợp
#     all_groups = Nhom.objects.filter(query).select_related('nguoi_tao').order_by('ten_nhom')
#
#     # Lấy danh sách nhóm đã tham gia
#     joined_memberships = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).values_list('ma_nhom', flat=True)
#     joined_groups = all_groups.filter(id__in=joined_memberships)
#
#     # Lấy danh sách nhóm đang chờ duyệt
#     pending_memberships = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='ChoDuyet'
#     ).values_list('ma_nhom', flat=True)
#     pending_groups = all_groups.filter(id__in=pending_memberships)
#
#     # Lấy danh sách nhóm chưa tham gia
#     unjoined_groups = all_groups.exclude(id__in=joined_memberships).exclude(id__in=pending_memberships)
#
#     # Lấy danh sách nhóm cho sidebar
#     nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).select_related('ma_nhom')
#     admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom', flat=True)
#     nhom_da_tham_gia = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).exclude(ma_nhom__in=admin_group_ids).select_related('ma_nhom')
#
#     context = {
#         'nguoi_dung': nguoi_dung,
#         'joined_groups': joined_groups,
#         'pending_groups': pending_groups,
#         'unjoined_groups': unjoined_groups,
#         'search_query': search_query,
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'nhom_lam_qtrivien': nhom_lam_qtrivien,
#     }
#
#     if not all_groups.exists():
#         context['error_message'] = f'Không tìm thấy nhóm nào với từ khóa "{search_query}"'
#
#     return render(request, 'social/Nhom/group_search_results.html', context)
import os

@login_required
def update_group_avatar(request, ma_nhom):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ.'})

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    nguoi_dung = request.user.nguoidung  # Kiểm tra dòng này

    # Kiểm tra quyền quản trị viên
    is_admin = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).exists()

    if not is_admin:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền cập nhật ảnh đại diện của nhóm này.'})

    if 'avatar' not in request.FILES:
        return JsonResponse({'success': False, 'message': 'Vui lòng chọn một file ảnh.'})

    avatar = request.FILES['avatar']

    # Xóa ảnh cũ nếu có
    if nhom.avatar and os.path.isfile(nhom.avatar.path):
        os.remove(nhom.avatar.path)

    # Lưu ảnh mới
    nhom.avatar = avatar
    nhom.save()

    return JsonResponse({
        'success': True,
        'avatar_url': nhom.avatar.url
    })
@login_required
def search_groups(request):
    search_query = request.GET.get('search', '')
    nguoi_dung = request.user.nguoidung

    # Lấy tất cả các nhóm cho khu vực chính (lọc theo từ khóa)
    all_groups = Nhom.objects.all()
    if search_query:
        all_groups = all_groups.filter(ten_nhom__icontains=search_query)
    else:
        all_groups = Nhom.objects.none()

    # Lấy danh sách nhóm mà người dùng làm quản trị viên (la_quan_tri_vien=True, trạng thái Được duyệt)
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'  # Đảm bảo nhóm đã được duyệt
    ).select_related('ma_nhom')
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)

    # Lấy danh sách nhóm đã tham gia (la_quan_tri_vien=False, trạng thái Được duyệt) cho khu vực chính
    joined_memberships = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=False,
        trang_thai='DuocDuyet'
    ).select_related('ma_nhom')
    if search_query:
        joined_memberships = joined_memberships.filter(ma_nhom__ten_nhom__icontains=search_query)
    else:
        joined_memberships = joined_memberships.none()
    joined_groups = [membership.ma_nhom for membership in joined_memberships]

    # Lấy danh sách nhóm đang chờ duyệt
    pending_memberships = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='ChoDuyet'
    ).select_related('ma_nhom')
    pending_group_ids = pending_memberships.values_list('ma_nhom_id', flat=True)
    pending_groups = Nhom.objects.filter(id__in=pending_group_ids)
    if search_query:
        pending_groups = pending_groups.filter(ten_nhom__icontains=search_query)
    else:
        pending_groups = Nhom.objects.none()

    # Lấy danh sách nhóm chưa tham gia
    unjoined_groups = all_groups.exclude(
        id__in=[membership.ma_nhom.id for membership in joined_memberships]
    ).exclude(id__in=pending_group_ids)

    # Lấy danh sách nhóm đã tham gia cho sidebar (không áp dụng bộ lọc search_query)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=False,
        trang_thai='DuocDuyet'
    ).select_related('ma_nhom')

    # Lấy danh sách nhóm làm quản trị viên cho sidebar (không áp dụng bộ lọc search_query)
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'  # Đảm bảo nhóm đã được duyệt
    ).select_related('ma_nhom')

    context = {
        'search_query': search_query,
        'joined_groups': joined_groups,
        'pending_groups': pending_groups,
        'unjoined_groups': unjoined_groups,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
    }
    return render(request, 'social/Nhom/group_search_results.html', context)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Nhom, ThanhVienNhom, NguoiDung
import json
import logging

# Thiết lập logging
logger = logging.getLogger(__name__)

@login_required
def join_group(request):
    if request.method != 'POST':
        logger.error("Phương thức không được hỗ trợ!")
        return JsonResponse({'success': False, 'error': 'Phương thức không được hỗ trợ!'}, status=405)

    try:
        data = json.loads(request.body)
        group_id = data.get('group_id')
        logger.info(f"Nhận yêu cầu tham gia nhóm với ID: {group_id}")

        if not group_id:
            logger.error("Không tìm thấy ID nhóm!")
            return JsonResponse({'success': False, 'error': 'Không tìm thấy ID nhóm!'}, status=400)

        nhom = get_object_or_404(Nhom, id=group_id)
        nguoi_dung = request.user.nguoidung
        logger.info(f"Người dùng {nguoi_dung.ho_ten} đang cố gắng tham gia nhóm {nhom.ten_nhom}")

        existing_membership = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung
        ).first()

        if existing_membership:
            if existing_membership.trang_thai == 'DuocDuyet':
                logger.warning(f"Người dùng {nguoi_dung.ho_ten} đã là thành viên của nhóm {nhom.ten_nhom}")
                return JsonResponse({'success': False, 'error': 'Bạn đã là thành viên của nhóm này!'}, status=400)
            elif existing_membership.trang_thai == 'ChoDuyet':
                logger.warning(f"Người dùng {nguoi_dung.ho_ten} đã gửi yêu cầu tham gia nhóm {nhom.ten_nhom}")
                return JsonResponse({'success': False, 'error': 'Bạn đã gửi yêu cầu tham gia rồi!'}, status=400)

        ThanhVienNhom.objects.create(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            trang_thai='ChoDuyet',
            la_quan_tri_vien=False
        )
        logger.info(f"Yêu cầu tham gia nhóm {nhom.ten_nhom} của {nguoi_dung.ho_ten} đã được tạo")
        return JsonResponse({'success': True, 'message': 'Yêu cầu tham gia nhóm đã được gửi!'})

    except Exception as e:
        logger.error(f"Lỗi khi xử lý yêu cầu tham gia nhóm: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# View cho trang chi tiết nhóm đã tham gia

@login_required
def nhom_da_tham_gia(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem nhóm đã tham gia!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('group')

    # Lấy danh sách nhóm mà người dùng làm quản trị viên
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')  # Bỏ values_list để trả về danh sách đối tượng

    # Lấy danh sách nhóm mà người dùng đã tham gia, loại trừ các nhóm làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai = 'DaDuyet'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    return render(request, 'social/Nhom/nhom_da_tham_gia.html', {
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nguoi_dung': nguoi_dung
    })

# View cho trang nhóm làm quản trị viên
@login_required
def nhom_lam_qtrivien(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem nhóm làm quản trị viên!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('group')

    # Lấy danh sách nhóm mà người dùng làm quản trị viên (chỉ nhóm đã duyệt trong cả ThanhVienNhom và Nhom)
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet',
    ).select_related('ma_nhom')

    # Lấy ID của các nhóm bạn làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)

    # Lấy danh sách nhóm đã tham gia, loại bỏ các nhóm mà người dùng làm quản trị viên, chỉ nhóm đã duyệt
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    # Thêm thông báo nếu không có nhóm làm quản trị viên
    if not nhom_lam_qtrivien.exists():
        messages.info(request, 'Bạn chưa làm quản trị viên của nhóm nào.')

    # Thêm thông báo nếu không có nhóm đã tham gia
    if not nhom_da_tham_gia.exists():
        messages.info(request, 'Bạn chưa tham gia nhóm nào ngoài vai trò quản trị viên.')

    context = {
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/Nhom/nhom_lam_qtrivien.html', context)
@login_required
def chi_tiet_nhom_dathamgia(request, ma_nhom):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem chi tiết nhóm!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
        return redirect('nhom_da_tham_gia')

    # Chỉ lấy nhóm đã duyệt
    nhom = get_object_or_404(Nhom, id=ma_nhom, trang_thai='DaDuyet')

    # Kiểm tra xem người dùng có phải thành viên đã duyệt không
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
        return redirect('nhom_da_tham_gia')

    # Lấy danh sách nhóm mà người dùng làm quản trị viên
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')

    # Lấy danh sách nhóm đã tham gia, loại trừ các nhóm làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    # Lấy danh sách bài viết trong nhóm
    posts = BaiViet.objects.filter(
        ma_nhom=nhom,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')

    posts_with_details = []
    for post in posts:
        word_count = len(post.noi_dung.strip().split())
        like_count = CamXuc.objects.filter(ma_bai_viet=post).count()
        has_liked = CamXuc.objects.filter(ma_bai_viet=post, ma_nguoi_dung=nguoi_dung).exists()
        posts_with_details.append({
            'post': post,
            'word_count': word_count,
            'like_count': like_count,
            'has_liked': has_liked
        })

    return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html', {
        'nhom': nhom,
        'posts_with_details': posts_with_details,
        'nguoi_dung': nguoi_dung,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien
    })

# @login_required
# def chi_tiet_nhom_quan_tri_vien(request, ma_nhom):
#     """View for group details page for administrators"""
#     try:
#         nguoi_dung = request.user.nguoidung
#     except:
#         messages.error(request, 'Không tìm thấy thông tin người dùng!')
#         return redirect('nhom_lam_qtrivien')
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#
#     # Check if user is an admin of this group
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
#         return redirect('nhom_lam_qtrivien')
#
#     # Get posts in the group
#     posts = BaiViet.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='DaDuyet'
#     ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')
#
#     # Process posts with details
#     posts_with_details = []
#     for post in posts:
#         word_count = len(post.noi_dung.strip().split())
#         like_count = CamXuc.objects.filter(ma_bai_viet=post).count()
#         has_liked = CamXuc.objects.filter(ma_bai_viet=post, ma_nguoi_dung=nguoi_dung).exists()
#
#         posts_with_details.append({
#             'post': post,
#             'word_count': word_count,
#             'like_count': like_count,
#             'has_liked': has_liked
#         })
#
#     # Get groups where user is admin
#     nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).select_related('ma_nhom')
#
#     # Get groups where user is a member but not admin
#     admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
#     nhom_da_tham_gia = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')
#
#     danh_sach_ban_be = NguoiDung.objects.exclude(user=nguoi_dung.user).all()
#
#     context = {
#         'nhom': nhom,
#         'posts_with_details': posts_with_details,
#         'nguoi_dung': nguoi_dung,
#         'danh_sach_ban_be': danh_sach_ban_be,
#         'nhom_lam_qtrivien': nhom_lam_qtrivien,
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'is_admin': True,  # Người dùng đã qua kiểm tra quyền, nên chắc chắn là admin
#     }
#
#     return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', context)

@login_required
def chi_tiet_nhom_quan_tri_vien(request, ma_nhom):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, id=ma_nhom)

    # Kiểm tra xem người dùng có phải là quản trị viên của nhóm này không
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
        return redirect('nhom_lam_qtrivien')

    # Lấy danh sách bài viết trong nhóm
    posts = BaiViet.objects.filter(
        ma_nhom=nhom,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')

    posts_with_details = []
    for post in posts:
        word_count = len(post.noi_dung.strip().split())
        like_count = CamXuc.objects.filter(ma_bai_viet=post).count()
        has_liked = CamXuc.objects.filter(ma_bai_viet=post, ma_nguoi_dung=nguoi_dung).exists()
        posts_with_details.append({
            'post': post,
            'word_count': word_count,
            'like_count': like_count,
            'has_liked': has_liked
        })

    # Lấy danh sách nhóm mà người dùng là quản trị viên
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')

    # Lấy danh sách nhóm mà người dùng là thành viên nhưng không phải quản trị viên, chỉ lấy nhóm đã duyệt
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'  # Thêm điều kiện lọc trạng thái nhóm
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    # Lấy danh sách thành viên của nhóm
    members = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='DuocDuyet'
    ).select_related('ma_nguoi_dung')

    # Lấy danh sách thành viên đang chờ duyệt
    pending_members = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='ChoDuyet'
    ).select_related('ma_nguoi_dung')

    danh_sach_ban_be = NguoiDung.objects.exclude(user=nguoi_dung.user).all()

    context = {
        'nhom': nhom,
        'posts_with_details': posts_with_details,
        'nguoi_dung': nguoi_dung,
        'danh_sach_ban_be': danh_sach_ban_be,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'members': members,
        'pending_members': pending_members,
        'is_admin': True,
    }

    return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', context)
@login_required
@require_POST
def gui_moi(request, ma_nhom):
    logger.info(f"Request body: {request.body}")
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền mời thành viên!'}, status=403)

    try:
        du_lieu = json.loads(request.body)
        user_id = du_lieu.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy ID người dùng!'}, status=400)

        try:
            ban_be = NguoiDung.objects.get(user__id=user_id)
            LoiMoiNhom.objects.update_or_create(
                ma_nhom=nhom,
                ma_nguoi_nhan=ban_be,
                defaults={'ma_nguoi_gui': nguoi_dung, 'trang_thai': 'ChoDuyet', 'thoi_gian_gui': timezone.now()}
            )
            return JsonResponse({'success': True, 'message': 'Lời mời đã được gửi!'})
        except NguoiDung.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy người dùng để mời!'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Dữ liệu không hợp lệ!'}, status=400)

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from .models import BaiViet, PollOption, PollVote
#
#
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Nhom, ThanhVienNhom, CamXuc, BinhLuan


from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction, connection
from .models import Nhom, ThanhVienNhom, BaiViet, BinhLuan, CamXuc
# import logging
# from .models import Nhom, ThanhVienNhom, BaiViet, BinhLuan, CamXuc, LoiMoiNhom, PollVote, ThongBao
# logger = logging.getLogger(__name__)

# @login_required
# def delete_group(request, ma_nhom):
#     response = {'success': False, 'message': 'Lỗi không xác định'}
#
#     if not request.user.is_authenticated:
#         response['message'] = 'Người dùng chưa đăng nhập!'
#         logger.warning('Unauthorized access to delete_group for ma_nhom=%s', ma_nhom)
#         return JsonResponse(response, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except Exception as e:
#         response['message'] = f'Không tìm thấy thông tin người dùng: {str(e)}'
#         logger.error('Failed to get nguoi_dung for user %s: %s', request.user.username, str(e))
#         return JsonResponse(response, status=403)
#
#     try:
#         nhom = get_object_or_404(Nhom, id=ma_nhom)
#         thanh_vien = ThanhVienNhom.objects.filter(
#             ma_nguoi_dung=nguoi_dung,
#             ma_nhom=nhom,
#             la_quan_tri_vien=True,
#             trang_thai='DuocDuyet'
#         ).first()
#
#         if not thanh_vien:
#             response['message'] = 'Bạn không có quyền xóa nhóm này!'
#             logger.warning('User %s attempted to delete group %s without admin rights', nguoi_dung.user.id, ma_nhom)
#             return JsonResponse(response, status=403)
#
#         logger.info('Starting deletion process for group %s by user %s', ma_nhom, nguoi_dung.user.id)
#
#         with transaction.atomic():
#             # Xóa PollVote nếu tồn tại
#             poll_vote_count = PollVote.objects.filter(ma_bai_viet__ma_nhom=nhom).count()
#             PollVote.objects.filter(ma_bai_viet__ma_nhom=nhom).delete()
#             logger.debug('Deleted %d PollVote records', poll_vote_count)
#
#             # Xóa lượt thích
#             cam_xuc_count = CamXuc.objects.filter(ma_bai_viet__ma_nhom=nhom).count()
#             CamXuc.objects.filter(ma_bai_viet__ma_nhom=nhom).delete()
#             logger.debug('Deleted %d CamXuc records', cam_xuc_count)
#
#             # Xóa bình luận
#             binh_luan_count = BinhLuan.objects.filter(ma_bai_viet__ma_nhom=nhom).count()
#             BinhLuan.objects.filter(ma_bai_viet__ma_nhom=nhom).delete()
#             logger.debug('Deleted %d BinhLuan records', binh_luan_count)
#
#             # Xóa bài viết
#             bai_viet_count = BaiViet.objects.filter(ma_nhom=nhom).count()
#             BaiViet.objects.filter(ma_nhom=nhom).delete()
#             logger.debug('Deleted %d BaiViet records', bai_viet_count)
#
#             # Xóa thông báo liên quan đến nhóm
#             thong_bao_count = ThongBao.objects.filter(loai='Nhom', lien_ket=f'/group/{ma_nhom}/').count()
#             ThongBao.objects.filter(loai='Nhom', lien_ket=f'/group/{ma_nhom}/').delete()
#             logger.debug('Deleted %d ThongBao records', thong_bao_count)
#
#             # Xóa thành viên
#             thanh_vien_count = ThanhVienNhom.objects.filter(ma_nhom=nhom).count()
#             ThanhVienNhom.objects.filter(ma_nhom=nhom).delete()
#             logger.debug('Deleted %d ThanhVienNhom records', thanh_vien_count)
#
#             # Xóa lời mời
#             loi_moi_count = LoiMoiNhom.objects.filter(ma_nhom=nhom).count()
#             LoiMoiNhom.objects.filter(ma_nhom=nhom).delete()
#             logger.debug('Deleted %d LoiMoiNhom records', loi_moi_count)
#
#             # Xóa nhóm
#             nhom.delete()
#             logger.info('Successfully deleted group %s', ma_nhom)
#
#         response = {'success': True, 'message': 'Nhóm đã được xóa thành công!'}
#         return JsonResponse(response)
#
#     except Exception as e:
#         response['message'] = f'Có lỗi xảy ra khi xóa nhóm: {str(e)}'
#         logger.error('Error deleting group %s by user %s: %s', ma_nhom, nguoi_dung.user.id if 'nguoi_dung' in locals() else 'unknown', str(e))
#         return JsonResponse(response, status=500)
import logging

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Nhom, ThanhVienNhom, CamXuc, BinhLuan
import logging

logger = logging.getLogger(__name__)

@login_required
def delete_group(request, ma_nhom):
    """View for deleting a group"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

    try:
        nguoi_dung = request.user.nguoidung
        nhom = get_object_or_404(Nhom, id=ma_nhom)

        # Check if the user is an admin of the group
        thanh_vien = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).first()

        if not thanh_vien:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa nhóm này!'}, status=403)

        # Delete related objects
        for bai_viet in BaiViet.objects.filter(ma_nhom=nhom):
            CamXuc.objects.filter(ma_bai_viet=bai_viet).delete()
            BinhLuan.objects.filter(ma_bai_viet=bai_viet).delete()
            PollOption.objects.filter(bai_viet=bai_viet).delete() # Delete poll options
            bai_viet.delete()

        ThanhVienNhom.objects.filter(ma_nhom=nhom).delete()
        LoiMoiNhom.objects.filter(ma_nhom=nhom).delete()

        # Finally, delete the group
        nhom.delete()

        return JsonResponse({'success': True, 'message': 'Nhóm đã được xóa thành công!'})

    except Nhom.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Nhóm không tồn tại!'}, status=404)
    except Exception as e:
        logger.exception("Error deleting group")
        return JsonResponse({'success': False, 'message': f'Có lỗi xảy ra khi xóa nhóm: {str(e)}'}, status=500)
@login_required
@require_GET
def duyet_thanh_vien(request, ma_nhom):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để phê duyệt thành viên!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền phê duyệt thành viên!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    pending_members = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='ChoDuyet'
    ).select_related('ma_nguoi_dung')

    return render(request, 'social/Nhom/duyet_thanh_vien.html', {
        'nhom': nhom,  # Đảm bảo nhom được truyền vào
        'pending_members': pending_members,
        'nguoi_dung': nguoi_dung
    })
@login_required
@require_POST
def duyet_thanh_vien_xac_nhan(request, ma_nhom, ma_thanh_vien):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)

        try:
            nguoi_dung = request.user.nguoidung
        except AttributeError:
            return JsonResponse({'success': False, 'message': 'Tài khoản người dùng chưa được thiết lập!'}, status=403)

        nhom = get_object_or_404(Nhom, id=ma_nhom)
        thanh_vien = ThanhVienNhom.objects.filter(
            ma_nguoi_dung=nguoi_dung,
            ma_nhom=nhom,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).first()

        if not thanh_vien:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt thành viên!'}, status=403)

        thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, id=ma_thanh_vien)
        thanh_vien_can_duyet.trang_thai = 'DuocDuyet'
        thanh_vien_can_duyet.save()

        return JsonResponse({'success': True, 'message': 'Thành viên đã được phê duyệt!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Lỗi server: {str(e)}'}, status=500)
@login_required
@require_POST
def tu_choi_thanh_vien(request, ma_nhom, ma_thanh_vien):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối thành viên!'}, status=403)

    thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, id=ma_thanh_vien)
    thanh_vien_can_duyet.delete()

    return JsonResponse({'success': True, 'message': 'Yêu cầu tham gia đã bị từ chối!'})
# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Nhom, ThanhVienNhom, BaiViet, ThongBao
import logging

logger = logging.getLogger(__name__)

@login_required
@require_POST
def duyet_bai_viet_action(request, ma_nhom):
    try:
        # Kiểm tra người dùng
        try:
            nguoi_dung = request.user.nguoidung
            logger.debug(f"Người dùng: {nguoi_dung.ho_ten} ({nguoi_dung.email})")
        except AttributeError:
            logger.error("Không tìm thấy thông tin người dùng!")
            return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=403)

        # Kiểm tra nhóm
        nhom = get_object_or_404(Nhom, id=ma_nhom)
        logger.debug(f"Nhóm: {nhom.id}, {nhom.ten_nhom}")

        # Kiểm tra quyền quản trị viên
        thanh_vien = ThanhVienNhom.objects.filter(
            ma_nguoi_dung=nguoi_dung,
            ma_nhom=nhom,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).first()
        if not thanh_vien:
            logger.error("Người dùng không có quyền phê duyệt!")
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết!'}, status=403)

        # Lấy post_id từ form
        post_id = request.POST.get('post_id')
        if not post_id:
            logger.error("Thiếu post_id!")
            return JsonResponse({'success': False, 'message': 'Thiếu thông tin bài viết!'}, status=400)

        # Kiểm tra action
        action = request.POST.get('action')
        if action not in ['approve', 'reject']:
            logger.error(f"Hành động không hợp lệ: {action}")
            return JsonResponse({'success': False, 'message': 'Hành động không hợp lệ!'}, status=400)

        # Lấy bài viết
        bai_viet = get_object_or_404(BaiViet, id=post_id, ma_nhom=nhom)
        logger.debug(f"Bài viết: {bai_viet.id}, Người đăng: {bai_viet.ma_nguoi_dung.ho_ten}")

        # Xử lý action
        if action == 'approve':
            bai_viet.trang_thai = 'DaDuyet'
            bai_viet.save()
            logger.info(f"Bài viết {post_id} đã được duyệt.")
            ThongBao.objects.create(
                ma_nguoi_nhan=bai_viet.ma_nguoi_dung,
                noi_dung=f"Bài viết của bạn trong nhóm {nhom.ten_nhom} đã được phê duyệt.",
                loai='BaiViet',
                lien_ket=reverse('chi_tiet_nhom_qtrivien', args=[nhom.id])
            )
            return JsonResponse({'success': True, 'message': 'Bài viết đã được phê duyệt!'})

        elif action == 'reject':
            reason = request.POST.get('reason', 'Không có lý do cụ thể.')
            logger.info(f"Bài viết {post_id} bị từ chối với lý do: {reason}")

            # Kiểm tra ma_nguoi_dung của bài viết
            if not bai_viet.ma_nguoi_dung:
                logger.error("Không tìm thấy người đăng bài viết!")
                return JsonResponse({'success': False, 'message': 'Không tìm thấy người đăng bài viết!'}, status=500)

            # Tạo thông báo
            try:
                lien_ket = reverse('chi_tiet_nhom_qtrivien', args=[nhom.id])
                ThongBao.objects.create(
                    ma_nguoi_nhan=bai_viet.ma_nguoi_dung,
                    noi_dung=f"Bài viết của bạn trong nhóm {nhom.ten_nhom} đã bị từ chối. Lý do: {reason}",
                    loai='BaiViet',
                    lien_ket=lien_ket
                )
                logger.debug("Tạo thông báo thành công.")
            except Exception as e:
                logger.error(f"Lỗi khi tạo thông báo: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': f'Lỗi khi tạo thông báo: {str(e)}'}, status=500)

            # Xóa các đối tượng liên quan bằng SQL thô
            try:
                with connection.cursor() as cursor:
                    # Xóa cảm xúc
                    cursor.execute("DELETE FROM social_camxuc WHERE ma_bai_viet_id = %s", [post_id])
                    logger.debug(f"Đã xóa cảm xúc liên quan đến bài viết {post_id}.")
                    # Xóa bình luận
                    cursor.execute("DELETE FROM social_binhluan WHERE ma_bai_viet_id = %s", [post_id])
                    logger.debug(f"Đã xóa bình luận liên quan đến bài viết {post_id}.")
                    # Xóa bài viết
                    cursor.execute("DELETE FROM social_baiviet WHERE id = %s", [post_id])
                    logger.debug(f"Bài viết {post_id} đã được xóa.")
            except Exception as e:
                logger.error(f"Lỗi khi xóa bài viết hoặc đối tượng liên quan: {str(e)}", exc_info=True)
                return JsonResponse({'success': False, 'message': f'Lỗi khi xóa bài viết: {str(e)}'}, status=500)

            return JsonResponse({'success': True, 'message': 'Bài viết đã bị từ chối và xóa!'})

    except Exception as e:
        logger.error(f"Lỗi xử lý yêu cầu: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'message': f'Lỗi xử lý yêu cầu: {str(e)}'}, status=500)

def duyet_bai_viet(request, ma_nhom):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để phê duyệt bài viết!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền phê duyệt bài viết!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    danh_sach_bai_viet_cho_duyet = BaiViet.objects.filter(
        ma_nhom=nhom,
        trang_thai='ChoDuyet'
    ).select_related('ma_nguoi_dung')

    return render(request, 'social/Nhom/duyet_bai_viet.html', {
        'nhom': nhom,
        'danh_sach_bai_viet_cho_duyet': danh_sach_bai_viet_cho_duyet,
        'nguoi_dung': nguoi_dung
    })
# @login_required
# @require_POST
# def duyet_bai_viet_xac_nhan(request, ma_nhom, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,  # Sửa typo nếu có
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết!'}, status=403)
#
#     bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet, ma_nhom=nhom)
#     try:
#         bai_viet.trang_thai = 'DaDuyet'
#         bai_viet.save()
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': f'Lỗi khi lưu bài viết: {str(e)}'}, status=500)
#
#     return JsonResponse({'success': True, 'message': 'Bài viết đã được phê duyệt!'})
# @login_required
# @require_POST
# def tu_choi_bai_viet(request, ma_nhom, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối bài viết!'}, status=403)
#
#     bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet, ma_nhom=nhom)
#     bai_viet.delete()
#
#     return JsonResponse({'success': True, 'message': 'Bài viết đã bị từ chối và xóa!'})
import logging
logger = logging.getLogger(__name__)

@login_required
@require_GET
def thanh_vien_nhom(request, ma_nhom):
    logger.debug(f"Truy cập thanh_vien-nhom với ma_nhom={ma_nhom}, method={request.method}")
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem thành viên nhóm!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
        logger.debug(f"Người dùng hiện tại: {nguoi_dung.email}")
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền xem thành viên nhóm!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    members = ThanhVienNhom.objects.filter(
        ma_nhom_id=ma_nhom,
        trang_thai='DuocDuyet',
        ma_nguoi_dung__user__isnull=False  # Thay ma_nguoi_dung__id bằng ma_nguoi_dung__user
    ).select_related('ma_nguoi_dung')

    logger.debug(f"Render template với {members.count()} thành viên")
    return render(request, 'social/Nhom/thanh_vien_nhom.html', {'members': members, 'nhom': nhom})

@login_required
@require_POST
def xoa_thanh_vien(request, ma_nhom, member_id):
    logger.debug(f"Nhận yêu cầu xóa thành viên: ma_nhom={ma_nhom}, member_id={member_id}")

    try:
        nguoi_dung = request.user.nguoidung
        logger.debug(f"Người dùng hiện tại: {nguoi_dung.email}")
    except AttributeError:
        logger.error("Không tìm thấy thông tin người dùng!")
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('thanh_vien_nhom', ma_nhom=ma_nhom)

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    logger.debug(f"Nhóm: {nhom.id}, {nhom.ten_nhom}")

    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_nhom=nhom,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    logger.debug(f"Kiểm tra quyền quản trị: thanh_vien={thanh_vien}")
    if not thanh_vien:
        logger.error("Người dùng không có quyền xóa thành viên!")
        messages.error(request, 'Bạn không có quyền xóa thành viên!')
        return redirect('thanh_vien_nhom', ma_nhom=ma_nhom)

    thanh_vien_can_xoa = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        ma_nguoi_dung__user_id=member_id,  # Thay ma_nguoi_dung_id bằng ma_nguoi_dung__user_id
        trang_thai='DuocDuyet'
    ).first()

    logger.debug(f"Kiểm tra thành viên cần xóa: thanh_vien_can_xoa={thanh_vien_can_xoa}")
    if not thanh_vien_can_xoa:
        logger.error(f"Thành viên với user_id {member_id} không tồn tại trong nhóm!")
        messages.error(request, f'Thành viên với user_id {member_id} không tồn tại trong nhóm!')
        return redirect('thanh_vien_nhom', ma_nhom=ma_nhom)

    try:
        thanh_vien_can_xoa.delete()
        logger.debug(f"Đã xóa thành viên với user_id {member_id} khỏi nhóm {ma_nhom}")
        messages.success(request, 'Thành viên đã được xóa khỏi nhóm!')
    except Exception as e:
        logger.error(f"Lỗi khi xóa thành viên: {str(e)}")
        messages.error(request, f'Lỗi khi xóa: {str(e)}')

    return redirect('thanh_vien_nhom', ma_nhom=ma_nhom)

#Linh
# @login_required
# def group(request):
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})
#
#     # Phân luồng dựa trên vai trò
#     if nguoi_dung.vai_tro == 'Admin':
#         return redirect('admin_group')
#
#     # Lấy tất cả các nhóm mà người dùng tham gia (bao gồm cả làm quản trị viên)
#     all_joined_groups = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet',
#         ma_nhom__trang_thai='DaDuyet'  # Chỉ lấy nhóm đã được duyệt
#     ).select_related('ma_nhom')
#
#     # Tách riêng nhóm làm quản trị viên và nhóm thành viên thường
#     nhom_lam_qtrivien = all_joined_groups.filter(la_quan_tri_vien=True)
#     nhom_da_tham_gia = all_joined_groups.filter(la_quan_tri_vien=False)
#
#     # Lấy tất cả ID nhóm (cả quản trị viên và thành viên thường)
#     all_group_ids = all_joined_groups.values_list('ma_nhom_id', flat=True)
#
#     # Lấy tất cả bài viết từ các nhóm đã tham gia
#     if all_group_ids:
#         posts = BaiViet.objects.filter(
#             ma_nhom_id__in=all_group_ids,
#             trang_thai='DaDuyet'
#         ).select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related(
#             'binh_luan', 'cam_xuc', 'poll_options'
#         ).order_by('-thoi_gian_dang')
#     else:
#         posts = BaiViet.objects.none()
#         messages.info(request, 'Bạn chưa tham gia nhóm nào. Hãy tìm kiếm và tham gia các nhóm để xem bài viết.')
#
#     # Tính số từ cho mỗi bài viết và thông tin bổ sung
#     all_group_posts = []
#     for post in posts:
#         word_count = len(post.noi_dung.strip().split())
#
#         # Kiểm tra xem người dùng đã thích bài viết chưa
#         has_liked = CamXuc.objects.filter(ma_bai_viet=post, ma_nguoi_dung=nguoi_dung).exists()
#
#         # Đếm số lượt thích và bình luận
#         like_count = CamXuc.objects.filter(ma_bai_viet=post).count()
#         comment_count = BinhLuan.objects.filter(ma_bai_viet=post).count()
#
#         # Xử lý poll nếu có
#         poll_options = []
#         if post.post_type == 'poll':
#             options = PollOption.objects.filter(bai_viet=post)
#             for option in options:
#                 # Kiểm tra xem người dùng đã vote cho option này chưa
#                 voted = PollVote.objects.filter(
#                     bai_viet=post,
#                     ma_nguoi_dung=nguoi_dung,
#                     option=option
#                 ).exists()
#                 poll_options.append({
#                     'option': option,
#                     'voted': voted
#                 })
#
#         all_group_posts.append({
#             'post': post,
#             'word_count': word_count,
#             'has_liked': has_liked,
#             'like_count': like_count,
#             'comment_count': comment_count,
#             'poll_options': poll_options
#         })
#
#     # Lấy danh sách bài viết mà người dùng đã thích (để highlight trong template)
#     liked_posts = CamXuc.objects.filter(
#         ma_nguoi_dung=nguoi_dung
#     ).values_list('ma_bai_viet_id', flat=True)
#
#     context = {
#         'nguoi_dung': nguoi_dung,
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'nhom_lam_qtrivien': nhom_lam_qtrivien,
#         'all_group_posts': all_group_posts,  # Tất cả bài viết từ các nhóm
#         'liked_posts': list(liked_posts),
#         'show_modal': False
#     }
#     return render(request, 'social/group.html', context)
def group(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})

    # Phân luồng dựa trên vai trò
    if nguoi_dung.vai_tro == 'Admin':
        return redirect('admin_group')

    # Lấy danh sách nhóm bạn làm quản trị viên (chỉ nhóm đã duyệt)
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'  # Đảm bảo nhóm đã được duyệt
    ).select_related('ma_nhom')

    # Lấy ID của các nhóm bạn làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)

    # Lấy danh sách nhóm đã tham gia (không bao gồm nhóm bạn làm quản trị viên, chỉ nhóm đã duyệt)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'  # Đảm bảo nhóm đã được duyệt
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    # Lấy ID các nhóm đã tham gia
    joined_group_ids = nhom_da_tham_gia.values_list('ma_nhom_id', flat=True)

    # Lấy bài viết
    if joined_group_ids:
        # Nếu có tham gia nhóm, lấy bài viết từ các nhóm đã tham gia
        posts = BaiViet.objects.filter(
            ma_nhom_id__in=joined_group_ids,
            trang_thai='DaDuyet'
        )
    else:
        # Nếu không tham gia nhóm nào, lấy bài viết công khai (không thuộc nhóm)
        posts = BaiViet.objects.filter(
            ma_nhom__isnull=True,
            trang_thai='DaDuyet'
        )
        messages.info(request, 'Bạn chưa tham gia nhóm nào. Hiển thị các bài viết công khai.')

    # Tối ưu truy vấn với select_related và prefetch_related
    posts = posts.select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related('binh_luan', 'cam_xuc').order_by('-thoi_gian_dang')

    # Tính số từ cho mỗi bài viết
    posts_with_wordcount = [
        {
            'post': post,
            'word_count': len(post.noi_dung.strip().split())
        }
        for post in posts
    ]

    # Lấy danh sách bài viết mà người dùng đã thích
    liked_posts = nguoi_dung.camxuc_set.values_list('ma_bai_viet_id', flat=True)

    # Nếu không có bài viết, hiển thị thông báo
    if not posts_with_wordcount:
        messages.info(request, 'Hiện tại không có bài viết nào để hiển thị.')

    context = {
        'nguoi_dung': nguoi_dung,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'posts_with_wordcount': posts_with_wordcount,
        'liked_posts': liked_posts,
        'show_modal': False  # Giữ nguyên, có thể thay đổi nếu cần
    }
    return render(request, 'social/group.html', context)


# # View đăng bài viết
# @login_required
# @require_POST
# def post_article(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})
#
#     try:
#         data = json.loads(request.body)
#         group_id = int(data.get('group_id'))
#         content = data.get('content')
#         post_type = data.get('type')
#
#         if not content:
#             return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})
#
#         nhom = Nhom.objects.get(id=group_id)
#
#         # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
#         membership = ThanhVienNhom.objects.filter(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             trang_thai='DuocDuyet'
#         ).first()
#         if not membership:
#             return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})
#
#         # Tạo bài viết mới
#         bai_viet = BaiViet.objects.create(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             noi_dung=content,
#             thoi_gian_dang=timezone.now(),
#             trang_thai='ChoDuyet' if nhom.trang_thai_nhom == 'RiengTu' else 'DaDuyet'
#         )
#
#         response_data = {
#             'success': True,
#             'post_id': bai_viet.id,
#             'ho_ten': nguoi_dung.ho_ten,
#             'thoi_gian_dang': bai_viet.thoi_gian_dang.strftime('%d/%m/%Y %H:%M'),
#             'type': post_type,
#             'content': content
#         }
#         return JsonResponse(response_data)
#     except Nhom.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})
#
# # View thích bài viết
# @login_required
# def like_post(request, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'error': 'Người dùng chưa đăng nhập!'}, status=401)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#         bai_viet = BaiViet.objects.get(id=ma_bai_viet)
#         cam_xuc, created = CamXuc.objects.get_or_create(
#             ma_bai_viet=bai_viet,
#             ma_nguoi_dung=nguoi_dung
#         )
#         if not created:
#             cam_xuc.delete()
#             liked = False
#         else:
#             liked = True
#         count = CamXuc.objects.filter(ma_bai_viet=bai_viet).count()
#         return JsonResponse({
#             'SoLuongCamXuc': count,
#             'liked': liked
#         })
#     except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist):
#         return JsonResponse({'error': 'Invalid request'}, status=400)
#
# # View thêm bình luận
# @login_required
# def them_binh_luan(request, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'}, status=401)
#
#     if request.method == 'POST':
#         noi_dung = request.POST.get('noi_dung')
#         try:
#             nguoi_dung = request.user.nguoidung
#             bai_viet = BaiViet.objects.get(id=ma_bai_viet)
#             binh_luan = BinhLuan.objects.create(
#                 ma_bai_viet=bai_viet,
#                 ma_nguoi_dung=nguoi_dung,
#                 noi_dung=noi_dung,
#                 thoi_gian=timezone.now()
#             )
#             return JsonResponse({'success': True, 'ho_ten': nguoi_dung.ho_ten, 'noi_dung': noi_dung})
#         except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist) as e:
#             return JsonResponse({'success': False, 'error': str(e)})
#     return JsonResponse({'success': False, 'error': 'Method not allowed'})
#
# # View cho bảng tin nhóm
# @login_required
# def group_feed(request):
#     if not request.user.is_authenticated:
#         return render(request, 'social/Nhom/error.html', {'message': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})
#
#     thanh_vien_nhom = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).values_list('ma_nhom', flat=True)
#
#     posts = BaiViet.objects.filter(
#         ma_nhom__in=thanh_vien_nhom,
#         trang_thai='DaDuyet'
#     ).select_related('ma_nguoi_dung', 'ma_nhom').order_by('-thoi_gian_dang')
#
#     # Tạo danh sách bài viết với số từ
#     posts_with_wordcount = []
#     for post in posts:
#         word_count = len(post.noi_dung.strip().split())
#         posts_with_wordcount.append({
#             'post': post,
#             'word_count': word_count
#         })
#
#     context = {
#         'posts_with_wordcount': posts_with_wordcount,
#         'nguoi_dung': nguoi_dung,
#     }
#     return render(request, 'social/group.html', context)
# @login_required
# def group_list(request):
#     return render(request, 'social/group.html', {'show_modal': False})
# @login_required
# def tao_nhom_moi(request):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để tạo nhóm!')
#         return redirect('login')
#
#     if request.method == 'POST':
#         ten_nhom = request.POST.get('group_name')
#         mo_ta = request.POST.get('group_description')
#
#         if ten_nhom:
#             try:
#                 nguoi_dung = request.user.nguoidung
#             except NguoiDung.DoesNotExist:
#                 messages.error(request, 'Không tìm thấy thông tin người dùng. Vui lòng cập nhật hồ sơ.')
#                 return redirect('group')
#
#             # Tạo nhóm mới
#             nhom = Nhom.objects.create(
#                 ten_nhom=ten_nhom,
#                 mo_ta=mo_ta,
#                 trang_thai='ChoDuyet',
#                 nguoi_tao=nguoi_dung
#             )
#
#             # Thêm người tạo làm quản trị viên
#             ThanhVienNhom.objects.create(
#                 ma_nhom=nhom,
#                 ma_nguoi_dung=nguoi_dung,
#                 trang_thai='DuocDuyet',
#                 la_quan_tri_vien=True
#             )
#
#             messages.success(request, f'Nhóm "{ten_nhom}" đã được gửi yêu cầu tạo! Đang chờ duyệt.')
#             return redirect('group')
#         else:
#             messages.error(request, 'Vui lòng nhập tên nhóm!')
#             return redirect('group')
#
#     return redirect('group')
# @login_required
# def search_groups(request):
#     if not request.user.is_authenticated:
#         return render(request, 'social/Nhom/error.html', {'message': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})
#
#     joined_groups = []
#     pending_groups = []
#     unjoined_groups = []
#
#     search_query = request.GET.get('search', '').lower()
#     all_groups = Nhom.objects.filter(ten_nhom__icontains=search_query)
#
#     if not all_groups.exists():
#         return render(request, 'social/Nhom/group_search_results.html', {
#             'nguoi_dung': nguoi_dung,
#             'joined_groups': [],
#             'pending_groups': [],
#             'unjoined_groups': [],
#             'search_query': search_query,
#             'error_message': f'Không tìm thấy nhóm nào với từ khóa "{search_query}"'
#         })
#
#     joined_memberships = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).values_list('ma_nhom', flat=True)
#     joined_groups = all_groups.filter(id__in=joined_memberships)
#
#     pending_memberships = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='ChoDuyet'
#     ).values_list('ma_nhom', flat=True)
#     pending_groups = all_groups.filter(id__in=pending_memberships)
#
#     unjoined_groups = all_groups.exclude(id__in=joined_memberships).exclude(id__in=pending_memberships)
#
#     context = {
#         'nguoi_dung': nguoi_dung,
#         'joined_groups': joined_groups,
#         'pending_groups': pending_groups,
#         'unjoined_groups': unjoined_groups,
#         'search_query': search_query
#     }
#     return render(request, 'social/Nhom/group_search_results.html', context)
# @login_required
# @require_POST
# def join_group(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})
#
#     try:
#         nguoi_dung = request.user.nguoidung
#         group_id = int(json.loads(request.body).get('group_id'))
#         nhom = Nhom.objects.get(id=group_id)
#
#         existing_membership = ThanhVienNhom.objects.filter(ma_nhom=nhom, ma_nguoi_dung=nguoi_dung).first()
#         if existing_membership:
#             return JsonResponse({'success': False, 'error': 'Bạn đã gửi yêu cầu hoặc đã tham gia nhóm này!'})
#
#         ThanhVienNhom.objects.create(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             trang_thai='ChoDuyet'
#         )
#         return JsonResponse({'success': True})
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại!'})
#     except Nhom.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})
#
# # View cho trang chi tiết nhóm đã tham gia
# @login_required
# def chi_tiet_nhom_dathamgia(request, group_id):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để xem chi tiết nhóm!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng!')
#         return redirect('group_feed')
#
#     # Lấy thông tin nhóm
#     nhom = get_object_or_404(Nhom, id=group_id)
#
#     # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
#     membership = ThanhVienNhom.objects.filter(
#         ma_nhom=nhom,
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).first()
#     if not membership:
#         messages.error(request, 'Bạn không có quyền xem nhóm này vì chưa là thành viên được duyệt!')
#         return redirect('group_feed')
#
#     # Lấy danh sách bài viết của nhóm
#     posts = BaiViet.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='DaDuyet'
#     ).select_related('ma_nguoi_dung', 'ma_nhom').order_by('-thoi_gian_dang')
#
#     # Tạo danh sách bài viết với số từ
#     posts_with_wordcount = []
#     for post in posts:
#         word_count = len(post.noi_dung.strip().split())
#         posts_with_wordcount.append({
#             'post': post,
#             'word_count': word_count
#         })
#
#     context = {
#         'nhom': nhom,
#         'posts_with_wordcount': posts_with_wordcount,
#         'nguoi_dung': nguoi_dung,
#     }
#     return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html', context)
#
# # View cho trang nhóm đã tham gia
# @login_required
# def nhom_da_tham_gia(request):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để xem nhóm đã tham gia!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng!')
#         return redirect('group')
#
#     # Lấy danh sách nhóm mà người dùng đã tham gia
#     nhom_da_tham_gia = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).select_related('ma_nhom')
#
#     return render(request, 'social/Nhom/nhom_da_tham_gia.html', {
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'nguoi_dung': nguoi_dung
#     })
#
# # View cho trang nhóm làm quản trị viên
# @login_required
# def nhom_lam_qtrivien(request):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để xem nhóm làm quản trị viên!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng!')
#         return redirect('group')
#
#     # Lấy danh sách nhóm mà người dùng làm quản trị viên
#     nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).select_related('ma_nhom')
#
#     # Lấy danh sách nhóm đã tham gia, loại bỏ các nhóm mà người dùng làm quản trị viên
#     admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
#     nhom_da_tham_gia = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')
#
#     return render(request, 'social/Nhom/nhom_lam_qtrivien.html', {
#         'nhom_lam_qtrivien': nhom_lam_qtrivien,
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'nguoi_dung': nguoi_dung
#     })
# @login_required
# def chi_tiet_nhom_quan_tri_vien(request, ma_nhom):
#
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để xem chi tiết nhóm!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
#         return redirect('nhom_lam_qtrivien')
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
#         return redirect('nhom_lam_qtrivien')
#
#     danh_sach_bai_viet = BaiViet.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='DaDuyet'
#     ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')
#
#     danh_sach_bai_viet_chi_tiet = []
#     for bai_viet in danh_sach_bai_viet:
#         so_tu = len(bai_viet.noi_dung.strip().split())
#         da_thich = CamXuc.objects.filter(ma_bai_viet=bai_viet, ma_nguoi_dung=nguoi_dung).exists()
#         danh_sach_bai_viet_chi_tiet.append({
#             'bai_viet': bai_viet,
#             'so_tu': so_tu,
#             'so_luot_thich': CamXuc.objects.filter(ma_bai_viet=bai_viet).count(),
#             'da_thich': da_thich
#         })
#
#     danh_sach_ban_be = NguoiDung.objects.exclude(user=nguoi_dung.user).all()
#
#     return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', {
#         'nhom': nhom,
#         'danh_sach_bai_viet_chi_tiet': danh_sach_bai_viet_chi_tiet,
#         'nguoi_dung': nguoi_dung,
#         'danh_sach_ban_be': danh_sach_ban_be
#     })
# @login_required
# @require_POST
# def gui_binh_luan(request, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=401)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=400)
#
#     bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet)
#     noi_dung = request.POST.get('content')
#
#     if not noi_dung:
#         return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống!'}, status=400)
#
#     BinhLuan.objects.create(
#         ma_bai_viet=bai_viet,
#         ma_nguoi_dung=nguoi_dung,
#         noi_dung=noi_dung,
#         thoi_gian=timezone.now()
#     )
#
#     return JsonResponse({'success': True, 'message': 'Bình luận đã được gửi!'})
# @login_required
# @require_POST
# def gui_moi(request, ma_nhom):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền mời thành viên!'}, status=403)
#
#     du_lieu = json.loads(request.body)
#     danh_sach_ma_ban_be = du_lieu.get('friend_ids', [])
#
#     for ma_ban_be in danh_sach_ma_ban_be:
#         try:
#             ban_be = NguoiDung.objects.get(user__id=ma_ban_be)
#             LoiMoiNhom.objects.update_or_create(
#                 ma_nhom=nhom,
#                 ma_nguoi_nhan=ban_be,
#                 defaults={'ma_nguoi_gui': nguoi_dung, 'trang_thai': 'ChoDuyet', 'thoi_gian_gui': timezone.now()}
#             )
#         except NguoiDung.DoesNotExist:
#             continue
#
#     return JsonResponse({'success': True, 'message': 'Lời mời đã được gửi!'})
# @login_required
# def duyet_thanh_vien(request, ma_nhom):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để phê duyệt thành viên!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
#         return redirect('nhom_lam_qtrivien')
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền phê duyệt thành viên!')
#         return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)
#
#     pending_members = ThanhVienNhom.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='ChoDuyet'
#     ).select_related('ma_nguoi_dung')
#
#     return render(request, 'social/Nhom/duyet_thanh_vien.html', {
#         'nhom': nhom,
#         'pending_members': pending_members,
#         'nguoi_dung': nguoi_dung
#     })
# @login_required
# @require_POST
# def duyet_thanh_vien_xac_nhan(request, ma_nhom, ma_thanh_vien):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt thành viên!'}, status=403)
#
#     thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, id=ma_thanh_vien)
#     thanh_vien_can_duyet.trang_thai = 'DuocDuyet'
#     thanh_vien_can_duyet.save()
#
#     return JsonResponse({'success': True, 'message': 'Thành viên đã được phê duyệt!'})
# @login_required
# @require_POST
# def tu_choi_thanh_vien(request, ma_nhom, ma_thanh_vien):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối thành viên!'}, status=403)
#
#     thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, id=ma_thanh_vien)
#     thanh_vien_can_duyet.delete()
#
#     return JsonResponse({'success': True, 'message': 'Yêu cầu tham gia đã bị từ chối!'})
# @login_required
# def duyet_bai_viet(request, ma_nhom):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để phê duyệt bài viết!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
#         return redirect('nhom_lam_qtrivien')
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền phê duyệt bài viết!')
#         return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)
#
#     danh_sach_bai_viet_cho_duyet = BaiViet.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='ChoDuyet'
#     ).select_related('ma_nguoi_dung')
#
#     return render(request, 'social/Nhom/duyet_bai_viet.html', {
#         'nhom': nhom,
#         'danh_sach_bai_viet_cho_duyet': danh_sach_bai_viet_cho_duyet,
#         'nguoi_dung': nguoi_dung
#     })
# @login_required
# @require_POST
# def duyet_bai_viet_xac_nhan(request, ma_nhom, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết!'}, status=403)
#
#     bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet, ma_nhom=nhom)
#     bai_viet.trang_thai = 'DaDuyet'
#     bai_viet.save()
#
#     return JsonResponse({'success': True, 'message': 'Bài viết đã được phê duyệt!'})
# @login_required
# @require_POST
# def tu_choi_bai_viet(request, ma_nhom, ma_bai_viet):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối bài viết!'}, status=403)
#
#     bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet, ma_nhom=nhom)
#     bai_viet.delete()
#
#     return JsonResponse({'success': True, 'message': 'Bài viết đã bị từ chối và xóa!'})
# @login_required
# def thanh_vien_nhom(request, ma_nhom):
#     if not request.user.is_authenticated:
#         messages.error(request, 'Bạn cần đăng nhập để xem thành viên nhóm!')
#         return redirect('login')
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Không tìm thấy thông tin người dùng trong hệ thống!')
#         return redirect('nhom_lam_qtrivien')
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền xem thành viên nhóm!')
#         return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)
#
#     members = ThanhVienNhom.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='DuocDuyet'
#     ).select_related('ma_nguoi_dung')
#
#     return render(request, 'social/Nhom/thanh_vien_nhom.html', {
#         'nhom': nhom,
#         'members': members,
#         'nguoi_dung': nguoi_dung
#     })
# @login_required
# @require_POST
# def xoa_thanh_vien(request, ma_nhom, ma_thanh_vien):
#     if not request.user.is_authenticated:
#         return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)
#
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)
#
#     nhom = get_object_or_404(Nhom, id=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nhom=nhom,
#         ma_nguoi_dung=nguoi_dung,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa thành viên!'}, status=403)
#
#     thanh_vien_can_xoa = get_object_or_404(ThanhVienNhom, id=ma_thanh_vien, ma_nhom=nhom)
#     thanh_vien_can_xoa.delete()
#
#     return JsonResponse({'success': True, 'message': 'Thành viên đã bị xóa khỏi nhóm!'})


@login_required
def profile(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng.')
        return redirect('login')
    return render(request, 'social/profile.html', {'nguoi_dung': nguoi_dung})

# Trang chủ
@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng.')
        return redirect('login')

    # Lấy bài viết công khai, đã duyệt, sắp xếp mới nhất lên trên
    posts = BaiViet.objects.filter(
        ma_nhom__isnull=True,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung').prefetch_related('cam_xuc', 'binh_luan', 'poll_options', 'poll_votes').order_by('-thoi_gian_dang')

    # Lấy danh sách bài viết đã thích
    liked_posts = CamXuc.objects.filter(
        ma_nguoi_dung=nguoi_dung
    ).values_list('ma_bai_viet_id', flat=True)

    context = {
        'posts': posts,
        'liked_posts': liked_posts,
        'nguoi_dung': nguoi_dung,
    }
    return render(request, 'social/home.html', context)

# Tạo bài viết công khai
@login_required
@require_POST
def create_post(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng'}, status=400)

    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.ma_nguoi_dung = nguoi_dung
        post.trang_thai = 'DaDuyet'  # Bài công khai không cần duyệt
        post.post_type = request.POST.get('post_type', 'text')
        post.save()

        # Xử lý thăm dò ý kiến
        if post.post_type == 'poll':
            option_count = 0
            for i in range(1, 11):  # Tối đa 10 lựa chọn
                option_text = request.POST.get(f'option_{i}')
                if option_text and option_text.strip():
                    PollOption.objects.create(bai_viet=post, text=option_text.strip())
                    option_count += 1
                if option_count >= 10:
                    break
            if option_count < 2:
                post.delete()
                return JsonResponse({'success': False, 'error': 'Thăm dò ý kiến cần ít nhất 2 lựa chọn'}, status=400)

        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'content': post.noi_dung,
            'post_type': post.post_type,
            'image_url': post.image.url if post.image else None,
            'video_url': post.video.url if post.video else None,
            'file_url': post.file.url if post.file else None,
        })
    else:
        return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)

# Like bài viết
@login_required
def like_post(request, ma_bai_viet):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Người dùng chưa đăng nhập!'}, status=401)

    try:
        nguoi_dung = request.user.nguoidung
        bai_viet = BaiViet.objects.get(id=ma_bai_viet)
        cam_xuc, created = CamXuc.objects.get_or_create(
            ma_bai_viet=bai_viet,
            ma_nguoi_dung=nguoi_dung
        )
        if not created:
            cam_xuc.delete()
            liked = False
        else:
            liked = True
        count = CamXuc.objects.filter(ma_bai_viet=bai_viet).count()
        return JsonResponse({
            'SoLuongCamXuc': count,
            'liked': liked
        })
    except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist):
        return JsonResponse({'error': 'Invalid request'}, status=400)

# Thêm bình luận
@login_required
@require_POST
def add_comment(request, post_id):
    try:
        post = BaiViet.objects.get(id=post_id)
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'success': False, 'error': 'Nội dung bình luận không được để trống'})
        comment = BinhLuan.objects.create(ma_nguoi_dung=request.user.nguoidung, ma_bai_viet=post, noi_dung=content)
        return JsonResponse({
            'success': True,
            'username': request.user.nguoidung.ho_ten,
            'content': comment.noi_dung,
            'created_at': comment.thoi_gian.strftime('%d/%m/%Y %H:%M')
        })
    except BaiViet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Lấy danh sách bình luận
@login_required
def get_comments(request, post_id):
    try:
        post = BaiViet.objects.get(id=post_id)
        comments = post.binh_luan.all().order_by('-thoi_gian')
        comments_data = [
            {
                'username': comment.ma_nguoi_dung.ho_ten,
                'content': comment.noi_dung,
                'created_at': comment.thoi_gian.strftime('%d/%m/%Y %H:%M')
            }
            for comment in comments
        ]
        return JsonResponse({'success': True, 'comments': comments_data})
    except BaiViet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Xóa bài viết
@login_required
@require_POST
def delete_post(request, post_id):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng'}, status=400)

    post = get_object_or_404(BaiViet, id=post_id, ma_nguoi_dung=nguoi_dung)
    post.delete()
    return JsonResponse({'success': True, 'message': 'Bài viết đã được xóa thành công'})

# Bình chọn thăm dò ý kiến
@login_required
@csrf_exempt
def vote_poll(request, post_id, option_id):
    """View for voting or unvoting on a poll, allowing multiple options per user"""
    logger.info(f"Processing vote/unvote for post_id={post_id}, option_id={option_id}")
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Phương thức không được phép!'}, status=405)

    try:
        # Kiểm tra bài viết và lựa chọn
        post = BaiViet.objects.get(id=post_id)
        if post.post_type != 'poll':
            return JsonResponse({'success': False, 'error': 'Bài viết không phải là thăm dò ý kiến!'}, status=400)

        option = PollOption.objects.get(bai_viet=post, id=option_id)

        # Kiểm tra người dùng
        user = request.user.nguoidung

        # Kiểm tra xem người dùng đã bình chọn cho option này chưa
        existing_vote = PollVote.objects.filter(
            bai_viet=post,
            ma_nguoi_dung=user,
            option=option
        ).first()

        voted_option_ids = list(PollVote.objects.filter(
            bai_viet=post,
            ma_nguoi_dung=user
        ).values_list('option_id', flat=True))

        if existing_vote:
            # Nếu đã vote cho option này, hủy vote
            existing_vote.delete()
            option.votes = max(0, option.votes - 1)  # Giảm số phiếu
            option.save()
            logger.info(f"User {user.ho_ten} unvoted option {option_id} for post {post_id}")
            voted_option_ids.remove(option.id)
        else:
            # Nếu chưa vote cho option này, tạo vote mới
            PollVote.objects.create(
                bai_viet=post,
                ma_nguoi_dung=user,
                option=option
            )
            option.votes += 1  # Tăng số phiếu
            option.save()
            logger.info(f"User {user.ho_ten} voted for option {option_id} for post {post_id}")
            voted_option_ids.append(option.id)

        # Lấy tổng số phiếu và dữ liệu các lựa chọn
        total_votes = PollVote.objects.filter(bai_viet=post).count()
        options = PollOption.objects.filter(bai_viet=post)
        votes_data = {str(opt.id): opt.votes for opt in options}

        return JsonResponse({
            'success': True,
            'total_votes': total_votes,
            'votes': votes_data,
            'voted_options': voted_option_ids  # Trả về danh sách các option đã vote
        })
    except BaiViet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại!'}, status=404)
    except PollOption.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lựa chọn không tồn tại!'}, status=404)
    except Exception as e:
        logger.error(f"Error in vote_poll: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_voters(request, option_id):
    """View for getting list of voters for a poll option"""
    try:
        option = PollOption.objects.get(id=option_id)
        voters = PollVote.objects.filter(option=option).select_related('ma_nguoi_dung')
        voters_list = [vote.ma_nguoi_dung.ho_ten for vote in voters]
        return JsonResponse({
            'success': True,
            'voters': voters_list
        })
    except PollOption.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lựa chọn không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Tìm kiếm
@login_required
def search(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    # Lấy tham số từ request
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('search_type', 'all')  # Mặc định là 'all' nếu không có tham số

    # Khởi tạo biến kết quả
    users = []
    posts = []

    if query:
        # Tìm kiếm người dùng nếu search_type là 'all' hoặc 'users'
        if search_type in ['all', 'users']:
            users = NguoiDung.objects.filter(
                Q(ho_ten__icontains=query) | Q(email__icontains=query)
            ).exclude(user=nguoi_dung.user).select_related('user')

        # Tìm kiếm bài viết nếu search_type là 'all' hoặc 'posts'
        if search_type in ['all', 'posts']:
            posts = BaiViet.objects.filter(
                Q(noi_dung__icontains=query) & Q(trang_thai='DaDuyet') & Q(ma_nhom__isnull=True)  # Chỉ lấy bài viết công khai
            ).select_related('ma_nguoi_dung').prefetch_related('poll_options', 'poll_votes').order_by('-thoi_gian_dang')

    # Xử lý yêu cầu AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'users': [
                {
                    'id': user.user.id,
                    'ho_ten': user.ho_ten,
                    'email': user.email,
                    'avatar': user.avatar.url if user.avatar else None
                } for user in users
            ],
            'posts': [
                {
                    'id': post.id,
                    'ma_nguoi_dung': {'ho_ten': post.ma_nguoi_dung.ho_ten},
                    'noi_dung': post.noi_dung,
                    'thoi_gian_dang': post.thoi_gian_dang.strftime('%d/%m/%Y %H:%M')
                } for post in posts
            ]
        })

    context = {
        'query': query,
        'search_type': search_type,
        'users': users,
        'posts': posts,
    }
    return render(request, 'social/search.html', context)



# View lấy thông tin chi tiết người dùng
@login_required
@require_GET
def get_user_details(request, user_id):
    logger.debug(f"Request received for get_user_details view: user_id={user_id}")
    try:
        user = get_object_or_404(User, id=user_id)
        nguoi_dung = user.nguoidung
        response_data = {
            'success': True,
            'ho_ten': nguoi_dung.ho_ten,
            'email': nguoi_dung.email,
            'diem_ngoai_khoa': nguoi_dung.diem_ngoai_khoa if nguoi_dung.vai_tro == 'SinhVien' else None,
            'avatar': nguoi_dung.avatar.url if nguoi_dung.avatar else None,
        }
        logger.debug(f"Returning user details for {nguoi_dung.ho_ten}")
        return JsonResponse(response_data)
    except NguoiDung.DoesNotExist:
        logger.error(f"User profile not found for user_id={user_id}")
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng'}, status=404)
    except Exception as e:
        logger.error(f"Error fetching user details for user_id={user_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




# @login_required
# def group(request):
#     try:
#         nguoi_dung = request.user.nguoidung
#     except NguoiDung.DoesNotExist:
#         return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})
#
#     # Phân luồng dựa trên vai trò
#     if nguoi_dung.vai_tro == 'Admin':
#         return redirect('admin_group')
#
#     # Lấy danh sách nhóm cho Sinh viên
#     nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         la_quan_tri_vien=True,
#         trang_thai='DuocDuyet'
#     ).select_related('ma_nhom')
#     admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
#     nhom_da_tham_gia = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='DuocDuyet'
#     ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')
#
#     # Lấy bài viết nhóm
#     posts = BaiViet.objects.filter(
#         ma_nhom__in=nhom_da_tham_gia.values('ma_nhom'),
#         trang_thai='DaDuyet'
#     ).select_related('ma_nguoi_dung', 'ma_nhom').order_by('-thoi_gian_dang')
#
#     posts_with_wordcount = []
#     for post in posts:
#         word_count = len(post.noi_dung.strip().split())
#         posts_with_wordcount.append({
#             'post': post,
#             'word_count': word_count
#         })
#
#     context = {
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'nhom_lam_qtrivien': nhom_lam_qtrivien,
#         'posts_with_wordcount': posts_with_wordcount,
#         'nguoi_dung': nguoi_dung,
#         'show_modal': False
#     }
#     return render(request, 'social/Nhom/group.html', context)

# Thông báo
@login_required
def notif(request):
    """View hiển thị danh sách thông báo"""
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return render(request, 'social/notif.html', {'thong_bao_list': []})

    # Lấy tất cả thông báo của người dùng, sắp xếp theo thời gian mới nhất
    # Chỉ select_related những trường thực sự tồn tại trong model
    thong_bao_list = ThongBao.objects.filter(
        ma_nguoi_nhan=nguoi_dung
    ).order_by('-thoi_gian')

    # Đánh dấu tất cả thông báo là đã đọc khi người dùng vào trang thông báo
    ThongBao.objects.filter(ma_nguoi_nhan=nguoi_dung, da_doc=False).update(da_doc=True)

    context = {
        'thong_bao_list': thong_bao_list,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/notif.html', context)


@login_required
def get_recent_notifications(request):
    """API để lấy thông báo gần đây (cho dropdown)"""
    try:
        nguoi_dung = request.user.nguoidung
        notifications = ThongBao.objects.filter(
            ma_nguoi_nhan=nguoi_dung
        ).order_by('-thoi_gian')[:10]  # Lấy 10 thông báo gần nhất

        notifications_data = []
        for notif in notifications:
            notifications_data.append({
                'id': notif.id,
                'noi_dung': notif.noi_dung,
                'loai': notif.loai,
                'da_doc': notif.da_doc,
                'thoi_gian': notif.thoi_gian.strftime('%d/%m/%Y %H:%M'),
                'lien_ket': notif.lien_ket
            })

        return JsonResponse({
            'success': True,
            'notifications': notifications_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Đăng nhập
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NguoiDung, Nhom, ThanhVienNhom, BaiViet, CamXuc, PollVote



@login_required
def group_view(request):
    try:
        nguoi_dung = request.user.nguoidung
        if nguoi_dung.vai_tro == 'Admin':
            return redirect('admin_group')  # Chuyển hướng admin đến trang quản lý nhóm
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    # Logic hiện tại để hiển thị trang nhóm cho sinh viên
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')

    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')

    group_ids = list(set(
        list(nhom_da_tham_gia.values_list('ma_nhom__id', flat=True)) +
        list(nhom_lam_qtrivien.values_list('ma_nhom__id', flat=True))
    ))

    all_group_posts = BaiViet.objects.filter(
        ma_nhom__id__in=group_ids,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related('poll_options', 'cam_xuc', 'binh_luan').order_by('-thoi_gian_dang')

    liked_posts = CamXuc.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_bai_viet__in=all_group_posts
    ).values_list('ma_bai_viet__id', flat=True)

    poll_votes = PollVote.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        bai_viet__in=all_group_posts
    ).select_related('option')

    voted_options = {vote.option.id for vote in poll_votes}

    posts_with_details = []
    for post in all_group_posts:
        poll_options = post.poll_options.all()
        for option in poll_options:
            option.voted = option.id in voted_options
        posts_with_details.append({
            'post': post,
            'word_count': len(post.noi_dung.split()),
            'poll_options': poll_options
        })

    if not posts_with_details:
        messages.info(request, 'Hiện tại không có bài viết nào trong các nhóm của bạn.')

    context = {
        'all_group_posts': posts_with_details,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nguoi_dung': nguoi_dung,
        'liked_posts': list(liked_posts),
    }
    return render(request, 'social/group.html', context)

# Đăng xuất
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')

# views.py

# Đăng ký
# Đăng ký (đã sửa lỗi)
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def register_view(request):
    logger.debug("Starting registration process")

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email').strip()
            password = form.cleaned_data.get('password')
            ho_ten = form.cleaned_data.get('ho_ten')
            logger.debug(f"Processing registration for email: {email}")

            # Kiểm tra định dạng email
            validator = EmailValidator()
            try:
                validator(email)
            except ValidationError:
                logger.warning(f"Invalid email format: {email}")
                messages.error(request, 'Email không hợp lệ. Vui lòng nhập email đúng định dạng.')
                return render(request, 'social/login/register.html', {'form': form})

            # Sử dụng giao dịch để kiểm tra và tạo bản ghi
            with transaction.atomic():
                # Kiểm tra email trong auth_user
                if User.objects.filter(email=email).exists():
                    logger.warning(f"Email already exists in auth_user: {email}")
                    messages.error(request, 'Email đã tồn tại. Vui lòng sử dụng email khác.')
                    return render(request, 'social/login/register.html', {'form': form})

                # Kiểm tra email trong NguoiDung
                if NguoiDung.objects.filter(email=email).exists():
                    logger.warning(f"Email already exists in NguoiDung: {email}")
                    messages.error(request, 'Email đã tồn tại. Vui lòng sử dụng email khác.')
                    return render(request, 'social/login/register.html', {'form': form})

                # Kiểm tra email đang chờ xác thực trong PendingRegistration
                if PendingRegistration.objects.filter(email=email, is_verified=False).exists():
                    logger.warning(f"Pending registration exists for email: {email}")
                    messages.error(request, 'Email này đã được đăng ký, vui lòng kiểm tra email để nhận mã OTP hoặc sử dụng email khác.')
                    return render(request, 'social/login/register.html', {'form': form})

                # Xóa các đăng ký tạm thời đã hết hạn
                PendingRegistration.objects.filter(
                    email=email,
                    expires_at__lt=timezone.now()
                ).delete()
                logger.debug(f"Deleted expired PendingRegistration for {email}")

                # Khởi tạo số lần gửi OTP ban đầu nếu chưa có
                if 'initial_otp_attempts' not in request.session:
                    request.session['initial_otp_attempts'] = 0

                # Giới hạn số lần gửi OTP ban đầu
                if request.session['initial_otp_attempts'] >= 3:
                    logger.warning(f"Max initial OTP attempts reached for {email}")
                    messages.error(request, 'Bạn đã vượt quá số lần gửi OTP. Vui lòng thử lại sau.')
                    if 'initial_otp_attempts' in request.session:
                        del request.session['initial_otp_attempts']
                    return render(request, 'social/login/register.html', {'form': form})

                # Tạo đăng ký tạm thời (không lưu mật khẩu và họ tên vào đây)
                pending_reg = PendingRegistration(
                    email=email,
                    password=password,
                    ho_ten=ho_ten)
                pending_reg.save()
                logger.debug(f"Created PendingRegistration for {email}")

                # Lưu thông tin tạm thời vào session
                request.session['pending_data'] = {
                    'email': email,
                    'password': password,
                    'ho_ten': ho_ten,
                }

                # Gửi email OTP
                subject = 'Xác nhận đăng ký tài khoản DUE Social'
                message = f'Mã xác nhận của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]

                try:
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    logger.info(f"OTP sent to {email}: {pending_reg.otp_code}")
                    request.session['register_email'] = email
                    request.session['otp_attempts'] = 0  # Khởi tạo số lần gửi lại OTP
                    request.session['otp_verify_attempts'] = 0  # Khởi tạo số lần nhập OTP sai
                    request.session['initial_otp_attempts'] += 1
                    messages.success(request, 'Mã OTP đã được gửi đến email của bạn.')
                    return redirect('verify_register_otp')
                except Exception as e:
                    logger.error(f"Failed to send OTP email to {email}: {str(e)}")
                    messages.error(request, f'Không thể gửi email: {str(e)}. Vui lòng thử lại.')
                    pending_reg.delete()
                    request.session['initial_otp_attempts'] += 1
                    if request.session['initial_otp_attempts'] >= 3:
                        if 'initial_otp_attempts' in request.session:
                            del request.session['initial_otp_attempts']
                    return render(request, 'social/login/register.html', {'form': form})

        else:
            logger.warning(f"Registration form invalid: {form.errors}")
            messages.error(request, f'Vui lòng kiểm tra lại thông tin nhập: {form.errors}')
            return render(request, 'social/login/register.html', {'form': form})

    else:
        form = RegisterForm()
        logger.debug("Rendering registration form")
    return render(request, 'social/login/register.html', {'form': form})

from django.db import transaction
#
#
# # Xác thực OTP (đăng ký)
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.models import User
# from django.db import transaction
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# def verify_register_otp_view(request):
#     logger.debug("Starting OTP verification for registration")
#
#     # Kiểm tra xem session có chứa thông tin cần thiết không
#     if 'register_email' not in request.session or 'pending_data' not in request.session:
#         logger.warning("No register_email or pending_data in session")
#         messages.error(request, 'Không tìm thấy thông tin đăng ký. Vui lòng đăng ký lại.')
#         return redirect('register')
#
#     # Khởi tạo số lần nhập OTP sai nếu chưa có
#     if 'otp_verify_attempts' not in request.session:
#         request.session['otp_verify_attempts'] = 0
#
#     if request.method == 'POST':
#         # Lấy mã OTP từ form (4 chữ số)
#         otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
#         entered_otp = ''.join(otp_digits)
#         logger.debug(f"Received OTP: {entered_otp}")
#
#         # Giới hạn số lần nhập OTP sai
#         if request.session['otp_verify_attempts'] >= 5:
#             logger.warning(f"Max OTP verify attempts reached for {request.session['register_email']}")
#             messages.error(request, 'Bạn đã nhập sai OTP quá nhiều lần. Vui lòng đăng ký lại.')
#             PendingRegistration.objects.filter(email=request.session['register_email']).delete()
#             # Xóa các session liên quan
#             for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
#                         'initial_otp_attempts']:
#                 if key in request.session:
#                     del request.session[key]
#             return redirect('register')
#
#         try:
#             # Lấy bản ghi PendingRegistration
#             pending_reg = PendingRegistration.objects.get(email=request.session['register_email'], is_verified=False)
#             logger.debug(f"Found PendingRegistration for {pending_reg.email}")
#
#             # Kiểm tra xem OTP có còn hợp lệ không (hết hạn)
#             if not pending_reg.is_valid():
#                 logger.warning(f"OTP expired for {pending_reg.email}")
#                 messages.error(request, 'Mã OTP đã hết hạn. Vui lòng đăng ký lại.')
#                 pending_reg.delete()
#                 for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
#                             'initial_otp_attempts']:
#                     if key in request.session:
#                         del request.session[key]
#                 return redirect('register')
#
#             # Kiểm tra mã OTP nhập vào
#             if pending_reg.otp_code != entered_otp:
#                 logger.warning(f"Invalid OTP for {pending_reg.email}: {entered_otp}")
#                 request.session['otp_verify_attempts'] += 1
#                 messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
#                 return render(request, 'social/login/verify_register_otp.html')
#
#             # Nếu OTP đúng, tiến hành tạo tài khoản
#             pending_data = request.session['pending_data']
#             email = pending_data['email']
#             password = pending_data['password']
#             ho_ten = pending_data['ho_ten']
#
#             # Sử dụng giao dịch nguyên tử để tạo User và NguoiDung
#             with transaction.atomic():
#                 # Tạo User
#                 user = User.objects.create_user(
#                     username=email,
#                     email=email,
#                     password=password,
#
#                 )
#                 if not user.is_active:
#                     logger.warning(f"User created but inactive: {user.email}")
#                     messages.error(request, 'Tài khoản được tạo nhưng không active. Vui lòng liên hệ admin.')
#                     user.delete()
#                     pending_reg.delete()
#                     for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
#                                 'initial_otp_attempts']:
#                         if key in request.session:
#                             del request.session[key]
#                     return redirect('register')
#
#                 logger.debug(f"Created User: {user.email}")
#                 # Đánh dấu PendingRegistration là đã xác minh
#                 pending_reg.is_verified = True
#                 pending_reg.save()
#
#                 # Xóa session sau khi hoàn tất
#                 for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
#                             'initial_otp_attempts']:
#                     if key in request.session:
#                         del request.session[key]
#
#                 logger.info(f"Registration completed for {pending_reg.email}")
#                 messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
#                 return redirect('login')
#
#         except PendingRegistration.DoesNotExist:
#             logger.warning("PendingRegistration not found or already verified")
#             messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')
#             return redirect('register')
#
#         except Exception as e:
#             logger.error(f"Unexpected error during OTP verification: {str(e)}")
#             messages.error(request, f'Đã xảy ra lỗi không mong muốn: {str(e)}. Vui lòng thử lại.')
#             # Xóa User nếu đã tạo mà lỗi xảy ra
#             if 'user' in locals():
#                 user.delete()
#             return redirect('register')
#
#     return render(request, 'social/login/verify_register_otp.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
import logging
from .models import PendingRegistration  # Đảm bảo import đúng

logger = logging.getLogger(__name__)

def verify_register_otp_view(request):
    logger.debug("Starting OTP verification for registration")

    # Kiểm tra xem session có chứa thông tin cần thiết không
    if 'register_email' not in request.session or 'pending_data' not in request.session:
        logger.warning("No register_email or pending_data in session")
        messages.error(request, 'Không tìm thấy thông tin đăng ký. Vui lòng đăng ký lại.')
        return redirect('register')

    # Khởi tạo số lần nhập OTP sai nếu chưa có
    if 'otp_verify_attempts' not in request.session:
        request.session['otp_verify_attempts'] = 0

    if request.method == 'POST':
        # Lấy mã OTP từ form (4 chữ số)
        otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
        entered_otp = ''.join(otp_digits)
        logger.debug(f"Received OTP: {entered_otp}")

        # Giới hạn số lần nhập OTP sai
        if request.session['otp_verify_attempts'] >= 5:
            logger.warning(f"Max OTP verify attempts reached for {request.session['register_email']}")
            messages.error(request, 'Bạn đã nhập sai OTP quá nhiều lần. Vui lòng đăng ký lại.')
            PendingRegistration.objects.filter(email=request.session['register_email']).delete()
            # Xóa các session liên quan
            for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
                       'initial_otp_attempts']:
                if key in request.session:
                    del request.session[key]
            return redirect('register')

        try:
            # Lấy bản ghi PendingRegistration
            pending_reg = PendingRegistration.objects.get(email=request.session['register_email'], is_verified=False)
            logger.debug(f"Found PendingRegistration for {pending_reg.email}")

            # Kiểm tra xem OTP có còn hợp lệ không (hết hạn)
            if not pending_reg.is_valid():
                logger.warning(f"OTP expired for {pending_reg.email}")
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng đăng ký lại.')
                pending_reg.delete()
                for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
                           'initial_otp_attempts']:
                    if key in request.session:
                        del request.session[key]
                return redirect('register')

            # Kiểm tra mã OTP nhập vào
            if pending_reg.otp_code != entered_otp:
                logger.warning(f"Invalid OTP for {pending_reg.email}: {entered_otp}")
                request.session['otp_verify_attempts'] += 1
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_register_otp.html')

            # Nếu OTP đúng, gọi verify_and_create_user để tạo User và NguoiDung
            with transaction.atomic():
                user = pending_reg.verify_and_create_user()
                if user is None:
                    logger.error(f"Failed to create user for {pending_reg.email}")
                    messages.error(request, 'Đã xảy ra lỗi khi tạo tài khoản. Vui lòng thử lại.')
                    pending_reg.delete()
                    return redirect('register')

                logger.debug(f"Created User and NguoiDung for {user.email}")
                # Xóa session sau khi hoàn tất
                for key in ['register_email', 'pending_data', 'otp_attempts', 'otp_verify_attempts',
                           'initial_otp_attempts']:
                    if key in request.session:
                        del request.session[key]

                logger.info(f"Registration completed for {pending_reg.email}")
                messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
                return redirect('login')

        except PendingRegistration.DoesNotExist:
            logger.warning("PendingRegistration not found or already verified")
            messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')
            return redirect('register')
        except Exception as e:
            logger.error(f"Unexpected error during OTP verification: {str(e)}")
            messages.error(request, f'Đã xảy ra lỗi không mong muốn: {str(e)}. Vui lòng thử lại.')
            return redirect('register')

    return render(request, 'social/login/verify_register_otp.html')
def verify_and_create_user(self):
    if self.is_valid():
        self.is_verified = True
        self.save()
        user, _ = User.objects.get_or_create(username=self.email, defaults={'email': self.email})
        user.set_password(self.password)
        user.save()
        nguoi_dung, _ = NguoiDung.objects.get_or_create(
            user=user,
            defaults={'ho_ten': self.ho_ten, 'email': self.email}
        )
        if not _.created:
            nguoi_dung.ho_ten = self.ho_ten
            nguoi_dung.save()
        return user
    return None



# Quên mk
def forgot_password_view(request):
    logger.debug("Starting forgot password process")
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            logger.warning("Forgot password attempt with empty email")
            messages.error(request, 'Vui lòng nhập email.')
            return render(request, 'social/login/forgot_password.html')

        # Kiểm tra định dạng email
        from django.core.validators import EmailValidator
        from django.core.exceptions import ValidationError
        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError:
            logger.warning(f"Invalid email format: {email}")
            messages.error(request, 'Email không hợp lệ. Vui lòng nhập email đúng định dạng.')
            return render(request, 'social/login/forgot_password.html')

        if not NguoiDung.objects.filter(email=email).exists():
            logger.warning(f"Email not found for forgot password: {email}")
            messages.error(request, 'Email không tồn tại trong hệ thống.')
            return render(request, 'social/login/forgot_password.html')

        # Xóa các OTP cũ cho email này
        OTP.objects.filter(email=email, is_used=False).delete()
        logger.debug(f"Deleted old OTPs for {email}")

        # Tạo OTP mới
        otp = OTP(
            email=email,
        )
        otp.save()
        logger.debug(f"Created OTP for {email}")

        # Gửi email OTP
        subject = 'Đặt lại mật khẩu DUE Social'
        message = f'Mã xác nhận của bạn là: {otp.otp_code}. Mã này có hiệu lực trong 10 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            logger.info(f"OTP sent to {email}: {otp.otp_code}")
            request.session['otp_email'] = email
            request.session['otp_attempts'] = 0  # Khởi tạo số lần gửi lại OTP
            messages.success(request, 'Mã OTP đã được gửi đến email của bạn.')
            return redirect('verify_otp')
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}")
            messages.error(request, f'Không thể gửi email: {str(e)}. Vui lòng thử lại.')
            otp.delete()
            return render(request, 'social/login/forgot_password.html')

    return render(request, 'social/login/forgot_password.html')

# Xác thực OTP (quên mật khẩu)
def verify_otp_view(request):
    logger.debug("Bắt đầu quá trình xác nhận OTP")
    if 'reset_email' not in request.session:
        logger.warning("Không tìm thấy reset_email trong session")
        messages.error(request, 'Không tìm thấy thông tin đặt lại mật khẩu. Vui lòng thử lại.')
        return redirect('forgot_password')

    email = request.session['reset_email']

    if request.method == 'POST':
        otp_code = ''.join([request.POST.get(f'otp{i}') for i in range(1, 5)])
        logger.debug(f"Nhận OTP: {otp_code} cho email: {email}")

        try:
            otp = OTP.objects.get(email=email, otp_code=otp_code, is_used=False)
            logger.debug(f"Tìm thấy OTP hợp lệ cho {email}")
        except OTP.DoesNotExist:
            logger.warning(f"OTP không hợp lệ hoặc đã hết hạn cho {email}")
            messages.error(request, 'Mã OTP không hợp lệ hoặc đã hết hạn.')
            return render(request, 'social/login/verify_otp.html')

        if not otp.is_valid():
            logger.warning(f"OTP đã hết hạn hoặc đã sử dụng cho {email}")
            messages.error(request, 'Mã OTP đã hết hạn hoặc đã được sử dụng.')
            return render(request, 'social/login/verify_otp.html')

        otp.is_used = True
        otp.save()
        logger.info(f"OTP xác nhận thành công cho {email}")
        messages.success(request, 'Xác nhận OTP thành công!')
        return redirect('reset_password')

    logger.debug("Hiển thị trang xác nhận OTP")
    return render(request, 'social/login/verify_otp.html')


# Gửi lại OTP (quên mật khẩu)
def resend_otp_view(request):
    logger.debug("Starting OTP resend process")
    if 'otp_email' not in request.session:
        logger.warning("No otp_email in session for resend")
        return redirect('forgot_password')

    email = request.session['otp_email']

    # Kiểm tra số lần gửi lại OTP
    otp_attempts = request.session.get('otp_attempts', 0)
    if otp_attempts >= 3:
        logger.warning(f"Max OTP resend attempts reached for {email}")
        messages.error(request, 'Bạn đã vượt quá số lần gửi lại OTP. Vui lòng thử lại sau.')
        del request.session['otp_email']
        del request.session['otp_attempts']
        return redirect('forgot_password')

    # Xóa OTP cũ
    OTP.objects.filter(email=email, is_used=False).delete()
    logger.debug(f"Deleted old OTPs for {email}")

    # Tạo OTP mới
    otp = OTP(
        email=email,
    )
    otp.save()
    logger.debug(f"Created new OTP for {email}")

    # Gửi email OTP
    subject = 'Đặt lại mật khẩu DUE Social'
    message = f'Mã xác nhận mới của bạn là: {otp.otp_code}. Mã này có hiệu lực trong 10 phút.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Resent OTP to {email}: {otp.otp_code}")
        request.session['otp_attempts'] = otp_attempts + 1
        messages.success(request, 'Đã gửi lại mã xác nhận. Vui lòng kiểm tra email của bạn.')
    except Exception as e:
        logger.error(f"Failed to resend OTP email to {email}: {str(e)}")
        messages.error(request, f'Không thể gửi email: {str(e)}')
        otp.delete()
        # Nếu gửi thất bại quá nhiều lần, xóa session
        request.session['otp_attempts'] = otp_attempts + 1
        if request.session['otp_attempts'] >= 3:
            logger.warning(f"Max OTP resend attempts reached after failure for {email}")
            del request.session['otp_email']
            del request.session['otp_attempts']

    return redirect('verify_otp')

# Danh sách sân sv
@login_required
def danh_sach_san(request):
    nguoi_dung = request.user.nguoidung
    if nguoi_dung.vai_tro == 'Admin':
        return redirect('danh_sach_san_admin')
    san_list = San.objects.all()
    return render(request, 'social/dat_lich/danh_sach_san.html', {'san_list': san_list})
# Lịch đặt sân
@login_required
def lich_dat_san_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để đặt lịch!')
        return redirect('login')

    location = request.GET.get('location')
    if not location:
        messages.error(request, 'Vui lòng chọn một sân!')
        return redirect('danh_sach_san')

    san = get_object_or_404(San, ten_san=location)
    nguoi_dung = request.user.nguoidung
    is_admin = nguoi_dung.vai_tro == 'Admin'

    if request.method == 'POST':
        bookings_json = request.POST.get('bookings')
        if bookings_json:
            try:
                bookings_data = json.loads(bookings_json)
                for booking in bookings_data:
                    date_str = booking.get('date')
                    time_str = booking.get('time')

                    if date_str and time_str:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        time_obj = datetime.strptime(time_str, '%H:%M').time()

                        # Kiểm tra slot đã được đặt chưa
                        if not DatLich.objects.filter(
                                ma_san=san,
                                ngay=date,
                                gio_bat_dau=time_obj,
                                trang_thai__in=['ChoDuyet', 'XacNhan']
                        ).exists():
                            DatLich.objects.create(
                                ma_san=san,
                                ma_nguoi_dung=nguoi_dung,
                                ngay=date,
                                gio_bat_dau=time_obj,
                                trang_thai='ChoDuyet'
                            )

                messages.success(request, 'Yêu cầu đặt lịch đã được gửi, chờ admin xác nhận!')
            except ValueError as e:
                messages.error(request, f'Lỗi định dạng ngày giờ: {e}')
            except Exception as e:
                messages.error(request, f'Lỗi khi lưu lịch: {e}')
        else:
            messages.error(request, 'Vui lòng chọn thời gian trước khi đặt lịch.')
        return redirect(f"{request.path}?location={location}")

    # Lấy ngày hiện tại và 6 ngày tiếp theo (tổng 7 ngày)
    today = datetime.now().date()
    days = []
    for i in range(7):
        current_date = today + timedelta(days=i)
        day_name = current_date.strftime("%A")  # Lấy tên thứ trong tuần

        # Chuyển đổi tên thứ sang tiếng Việt
        day_name_vi = {
            "Monday": "Thứ Hai",
            "Tuesday": "Thứ Ba",
            "Wednesday": "Thứ Tư",
            "Thursday": "Thứ Năm",
            "Friday": "Thứ Sáu",
            "Saturday": "Thứ Bảy",
            "Sunday": "Chủ Nhật"
        }.get(day_name, day_name)

        days.append({
            'name': day_name_vi,
            'date': current_date.strftime("%d/%m"),
            'full_date': current_date.strftime("%Y-%m-%d")
        })

    # Tạo danh sách giờ từ 7:00 đến 20:00
    times = [f"{hour:02d}:00" for hour in range(7, 21)]

    # Lấy danh sách lịch đã đặt cho sân này trong 7 ngày tới
    start_date = today
    end_date = today + timedelta(days=6)

    # Nếu là admin, lấy tất cả lịch đặt
    # Nếu là người dùng thường, chỉ lấy lịch đặt của họ
    if is_admin:
        bookings = DatLich.objects.filter(
            ma_san=san,
            ngay__gte=start_date,
            ngay__lte=end_date,
            trang_thai__in=['ChoDuyet', 'XacNhan']
        )
    else:
        # Người dùng thường chỉ thấy lịch của họ và các ô đã được đặt (không hiển thị thông tin người đặt)
        bookings = DatLich.objects.filter(
            ma_san=san,
            ngay__gte=start_date,
            ngay__lte=end_date,
            trang_thai__in=['ChoDuyet', 'XacNhan']
        )

    # Tạo cấu trúc dữ liệu cho lịch
    calendar_data = []
    for time in times:
        row = []
        for day in days:
            day_date = datetime.strptime(day['full_date'], '%Y-%m-%d').date()
            cell = {
                'date': day['full_date'],
                'time': time,
                'status': 'past' if day_date < today else 'available',
                'is_mine': False  # Mặc định không phải của người dùng hiện tại
            }

            # Kiểm tra xem ô này đã được đặt chưa
            for booking in bookings:
                if (booking.ngay == day_date and
                        booking.gio_bat_dau.strftime('%H:%M') == time):
                    cell['status'] = booking.trang_thai
                    # Đánh dấu nếu lịch này là của người dùng hiện tại
                    if booking.ma_nguoi_dung == nguoi_dung:
                        cell['is_mine'] = True
                    break

            row.append(cell)
        calendar_data.append(row)

    # Lịch của người dùng hiện tại
    user_bookings = DatLich.objects.filter(
        ma_san=san,
        ma_nguoi_dung=nguoi_dung,
        ngay__gte=today
    ).order_by('ngay', 'gio_bat_dau')

    context = {
        'location': location,
        'days': days,
        'times': times,
        'calendar_data': calendar_data,
        'user_bookings': user_bookings,
        'today': today.strftime('%Y-%m-%d'),
        'is_admin': is_admin
    }
    return render(request, 'social/dat_lich/lich_dat_san.html', context)

# Danh sách sân admin
@login_required
def danh_sach_san_admin(request):
    san_list = San.objects.all()
    return render(request, 'social/dat_lich_admin/danh_sach_san_admin.html', {'san_list': san_list})

#Chờ duyệt của admin
@login_required
def choduyet(request):
    if request.user.nguoidung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('lich_dat_san_view')

    location = request.GET.get('location')
    if not location:
        messages.error(request, 'Không tìm thấy địa điểm.')
        return redirect('danh_sach_san_admin')

    san = get_object_or_404(San, ten_san=location)

    # Lấy tất cả lịch có trạng thái 'ChoDuyet' cho sân này
    pendings = DatLich.objects.filter(ma_san=san, trang_thai='ChoDuyet').select_related('ma_nguoi_dung')

    context = {
        'pendings': pendings,
        'location': location,
    }
    return render(request, 'social/dat_lich_admin/Choduyet.html', context)

@login_required
def Xacnhan(request, pending_id):
    if request.user.nguoidung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('lich_dat_san_view')

    try:
        pending = DatLich.objects.get(id=pending_id, trang_thai='ChoDuyet')
        pending.trang_thai = 'XacNhan'
        pending.save()
        messages.success(request, 'Lịch đã được xác nhận thành công.')
    except DatLich.DoesNotExist:
        messages.error(request, 'Lịch không tồn tại hoặc đã được xử lý.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#hủy lịch
@login_required
def Huy(request, pending_id):
    if request.user.nguoidung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('lich_dat_san_view')

    try:
        pending = DatLich.objects.get(id=pending_id, trang_thai='ChoDuyet')
        pending.trang_thai = 'Huy'
        pending.save()
        messages.success(request, 'Lịch đã được hủy thành công.')
    except DatLich.DoesNotExist:
        messages.error(request, 'Lịch không tồn tại hoặc đã được xử lý.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# Xem danh sách lịch đã đặt
@login_required
def xemdanhsach_view (request):
    if request.user.nguoidung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('lich_dat_san_view')

    location = request.GET.get('location')
    if not location:
        return redirect('danh_sach_san_admin')

    san = get_object_or_404(San, ten_san=location)
    confirmed_schedules = DatLich.objects.filter(ma_san=san).exclude(trang_thai='ChoDuyet')
    return render(request, 'social/dat_lich_admin/Xemdanhsach.html', {
        'confirmed_schedules': confirmed_schedules,
        'location': location
    })

#Huỷ xem danh sách
@login_required
def HuyXemdanhsach(request, schedule_id):
    if request.user.nguoidung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('lich_dat_san_view')

    schedule = get_object_or_404(DatLich, id=schedule_id)
    schedule.trang_thai = "Huy"
    schedule.save()
    messages.success(request, "Lịch đã được hủy thành công.")
    return redirect('Xemdanhsach')

# Sinh viên ngoại khóa
def search_activities(request):
    if not request.user.is_authenticated:
        return redirect('login')

    nguoi_dung = request.user.nguoidung

    if request.method == "POST":
        ma_hd_nk = request.POST.get("ma_hd_nk")
        hoat_dong = HoatDongNgoaiKhoa.objects.get(id=ma_hd_nk)
        _, created = DKNgoaiKhoa.objects.get_or_create(
            ma_hd_nk=hoat_dong,
            ma_nguoi_dung=nguoi_dung,
            defaults={'trang_thai': 'DangKy'}
        )
        if created:
            messages.success(request, "Bạn đã đăng ký tham gia thành công!")
        else:
            messages.info(request, "Bạn đã đăng ký hoạt động này rồi.")

    activities = HoatDongNgoaiKhoa.objects.all().order_by('-thoi_gian')
    se_tham_gia, da_tham_gia = phan_loai_nk_SV(nguoi_dung)

    query = request.GET.get('q', '')
    if query:
        activity = HoatDongNgoaiKhoa.objects.filter(ten_hd_nk__icontains=query)
    else:
        activity = HoatDongNgoaiKhoa.objects.all()


    return render(request, 'social/Extracurricular/extra_searchResult.html', {
        'activity': activity,
        'query': query,
        'activities': activities,
        'se_tham_gia': se_tham_gia,
        'da_tham_gia': da_tham_gia,

    })

def admin_search_activities(request):
    if not request.user.is_authenticated or request.user.nguoidung.vai_tro != 'Admin':
        return redirect('login')

    nguoi_dung = request.user.nguoidung

    if request.method == 'POST':
        success, form = process_extracurricular_form(request, ExtracurricularForm, nguoi_dung)
        if success:
            return redirect('Extracurricular_admin')
    else:
        form = ExtracurricularForm()

    chua_dien_ra, da_dien_ra = phan_loai_nk_GV(request)
    activities = HoatDongNgoaiKhoa.objects.order_by('-thoi_gian')

    query = request.GET.get('q', '')
    if query:
        activity = HoatDongNgoaiKhoa.objects.filter(ten_hd_nk__icontains=query)
    else:
        activity = HoatDongNgoaiKhoa.objects.all()


    return render(request, 'social/Extracurricular_admin/admin_extra_searchResult.html', {
        'activity': activity,
        'query': query,
        'form': form,
        'nguoi_dung': nguoi_dung,
        'activities': activities,
        'chua_dien_ra': chua_dien_ra,
        'da_dien_ra': da_dien_ra
    })


@login_required
def phan_loai_nk_SV(nguoi_dung):
    now = timezone.now()

    # Lấy ID của các hoạt động "sẽ tham gia"
    se_tham_gia_ids = DKNgoaiKhoa.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DangKy',
        ma_hd_nk__thoi_gian__gt=now
    ).values_list('ma_hd_nk_id', flat=True)

    # Lấy ID của các hoạt động "đã tham gia"
    da_tham_gia_ids = DKNgoaiKhoa.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='ThamGia',
        ma_hd_nk__thoi_gian__lte=now
    ).values_list('ma_hd_nk_id', flat=True)

    # Truy vấn lại để lấy thông tin chi tiết hoạt động
    se_tham_gia = HoatDongNgoaiKhoa.objects.filter(id__in=se_tham_gia_ids)
    da_tham_gia = HoatDongNgoaiKhoa.objects.filter(id__in=da_tham_gia_ids)

    return se_tham_gia, da_tham_gia

@login_required
def extracurricular(request):
    if not request.user.is_authenticated:
        return redirect('login')

    nguoi_dung = request.user.nguoidung

    if request.method == "POST":
        ma_hd_nk = request.POST.get("ma_hd_nk")
        hoat_dong = HoatDongNgoaiKhoa.objects.get(id=ma_hd_nk)

        # Kiểm tra đã đăng ký chưa
        da_dang_ky = DKNgoaiKhoa.objects.filter(
            ma_hd_nk=hoat_dong,
            ma_nguoi_dung=nguoi_dung
        ).exists()

        if da_dang_ky:
            messages.info(request, "Bạn đã đăng ký hoạt động này rồi.")
        else:
            # Đếm số lượng đăng ký hiện tại
            so_luong_dk = DKNgoaiKhoa.objects.filter(ma_hd_nk=hoat_dong, trang_thai='DangKy').count()

            if so_luong_dk >= hoat_dong.so_luong:
                messages.error(request, "Hoạt động đã đủ số lượng. Không thể đăng ký thêm.")
            else:
                # Đăng ký mới
                DKNgoaiKhoa.objects.create(
                    ma_hd_nk=hoat_dong,
                    ma_nguoi_dung=nguoi_dung,
                    trang_thai='DangKy'
                )
                messages.success(request, "Bạn đã đăng ký tham gia thành công!")

    activities = HoatDongNgoaiKhoa.objects.all().order_by('-thoi_gian')
    se_tham_gia, da_tham_gia = phan_loai_nk_SV(nguoi_dung)
    return render(request, 'social/Extracurricular/extracurricular.html', {
        'activities': activities,
        'se_tham_gia': se_tham_gia,
        'da_tham_gia': da_tham_gia,
    })

@login_required
def extracurricular_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    nguoi_dung = request.user.nguoidung
    activity = get_object_or_404(HoatDongNgoaiKhoa, pk=pk)
    se_tham_gia, da_tham_gia = phan_loai_nk_SV(nguoi_dung)
    return render(request, 'social/Extracurricular/extracurricular_detail.html', {
        'activity': activity,
        'nguoi_dung': nguoi_dung,
        'se_tham_gia': se_tham_gia,
        'da_tham_gia': da_tham_gia,
    })

# Admin ngoại khóa
@login_required
def process_extracurricular_form(request, form_class, nguoi_dung):
    form = form_class(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.nguoi_tao = nguoi_dung
        instance.save()
        return True, form
    return False, form

from django.core.exceptions import ObjectDoesNotExist

@login_required
def phan_loai_nk_GV(request):

    if request.user.nguoidung.vai_tro != 'Admin':
        return None, None  # Hoặc raise PermissionDenied
    try:
        nguoi_dung = request.user.nguoidung
        # Lấy tất cả hoạt động do người dùng tạo
        activities = HoatDongNgoaiKhoa.objects.filter(nguoi_tao=nguoi_dung)
        now = timezone.now()
        chua_dien_ra =  activities.filter(thoi_gian__gt=now).order_by('thoi_gian')
        da_dien_ra =  activities.filter(thoi_gian__lte=now).order_by('-thoi_gian')
        return chua_dien_ra, da_dien_ra
    except ObjectDoesNotExist:
        return None, None  # Hoặc xử lý lỗi khác

@login_required
def admin_extracurr(request):
    if not request.user.is_authenticated or request.user.nguoidung.vai_tro != 'Admin':
        return redirect('login')

    nguoi_dung = request.user.nguoidung

    if request.method == 'POST':
        success, form = process_extracurricular_form(request, ExtracurricularForm, nguoi_dung)
        if success:
            return redirect('Extracurricular_admin')
    else:
        form = ExtracurricularForm()

    chua_dien_ra, da_dien_ra = phan_loai_nk_GV(request)
    activities = HoatDongNgoaiKhoa.objects.order_by('-thoi_gian')

    return render(request, 'social/Extracurricular_admin/admin_extracurr.html', {
        'form': form,
        'nguoi_dung': nguoi_dung,
        'activities': activities,
        'chua_dien_ra': chua_dien_ra,
        'da_dien_ra': da_dien_ra
    })

from django.contrib.auth.decorators import login_required
from .models import HoatDongNgoaiKhoa, DKNgoaiKhoa
from .forms import ExtracurricularForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def duyet_tat_ca_SV(request, activity):
    danh_sach_sv = request.POST.getlist('sinh_vien_duyet')
    if danh_sach_sv:
        DKNgoaiKhoa.objects.filter(
            id__in=danh_sach_sv,
            ma_hd_nk=activity
        ).update(trang_thai='ThamGia')
        return len(danh_sach_sv)
    return 0

@login_required
def duyet_tung_sinh_vien(request, id_dang_ky):
    try:
        dang_ky = DKNgoaiKhoa.objects.get(id=id_dang_ky)
        dang_ky.trang_thai = 'ThamGia'
        dang_ky.save()
        messages.success(request, f"Đã xác nhận tham gia cho sinh viên {dang_ky.ma_nguoi_dung.ho_ten}")
    except DKNgoaiKhoa.DoesNotExist:
        messages.error(request, "Không tìm thấy đăng ký sinh viên.")


@login_required
def admin_extracurr_detail(request, pk):
    # Kiểm tra quyền Admin
    if request.user.nguoidung.vai_tro != 'Admin':
        return redirect('login')

    # Lấy hoạt động theo ID
    activity = get_object_or_404(HoatDongNgoaiKhoa, pk=pk)
    nguoi_dung = request.user.nguoidung

    keyword = request.GET.get('search', '')  # ← Lấy keyword từ query string

    sinh_vien_dang_ky = DKNgoaiKhoa.objects.filter(ma_hd_nk=activity)
    # Nếu có keyword → lọc
    if keyword:
        sinh_vien_dang_ky = sinh_vien_dang_ky.filter(
            Q(ma_nguoi_dung__ho_ten__icontains=keyword) |
            Q(ma_nguoi_dung__email__icontains=keyword)
        )

    sinh_vien_list = []

    for dk in sinh_vien_dang_ky:
        sinh_vien_list.append({
            'ho_ten': dk.ma_nguoi_dung.ho_ten,
            'email': dk.ma_nguoi_dung.email,
            'trang_thai': dk.trang_thai,
            'ma_dk_nk': dk.id
        })

    so_luong_dk = sinh_vien_dang_ky.count()
    so_luong_da_tham_gia = sinh_vien_dang_ky.filter(trang_thai='ThamGia').count()

    if request.method == 'POST':
        if 'duyet_sinh_vien' in request.POST:
            id_dang_ky = request.POST.get('sinh_vien_duyet')
            duyet_tung_sinh_vien(request, id_dang_ky=id_dang_ky)
            return redirect('admin_extracurr_detail', pk=pk)


        elif 'duyet_all' in request.POST:
            so_duyet = duyet_tat_ca_SV(request, activity)
            messages.success(request, f"Đã duyệt {so_duyet} sinh viên.")
            return redirect('admin_extracurr_detail', pk=pk)

        else:
            success, form = process_extracurricular_form(request, ExtracurricularForm, request.user.nguoidung)
            if success:
                return redirect('Extracurricular_admin.html')
    else:
        form = ExtracurricularForm()

    chua_dien_ra, da_dien_ra = phan_loai_nk_GV(request)
    trang_thai_hoat_dong = (
        'chua_dien_ra' if activity in chua_dien_ra else
        'da_dien_ra' if activity in da_dien_ra else
        'khac'
    )

    return render(request, 'social/Extracurricular_admin/admin_extracurr_detail.html', {
        'activity': activity,
        'nguoi_dung': nguoi_dung,
        'sinh_vien_list': sinh_vien_list,
        'trang_thai_hoat_dong': trang_thai_hoat_dong,
        'so_luong_dk': so_luong_dk,
        'so_luong_da_tham_gia': so_luong_da_tham_gia,
        'chua_dien_ra': chua_dien_ra,
        'da_dien_ra': da_dien_ra,
        'form': form,
        'keyword': keyword
    })


@login_required
def admin_group(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    # Lấy danh sách nhóm
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).select_related('ma_nhom')
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    # Lấy bài viết nhóm
    posts = BaiViet.objects.filter(
        ma_nhom__in=nhom_da_tham_gia.values('ma_nhom'),
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung', 'ma_nhom').order_by('-thoi_gian_dang')

    context = {
        'posts': posts,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtri': nhom_lam_qtrivien,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/nhom_list.html', context)


# Nhóm admin
@login_required
@login_required
def nhom_list(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    groups = Nhom.objects.filter(trang_thai='DaDuyet').select_related('nguoi_tao')  # Lấy nhóm đã duyệt
    context = {
        'groups': groups,  # Truyền đúng biến groups
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/nhom_list.html', context)

@login_required
def nhom_detail(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    nhom = get_object_or_404(Nhom, id=nhom_id)
    posts = BaiViet.objects.filter(ma_nhom=nhom, trang_thai='DaDuyet').select_related('ma_nguoi_dung').order_by(
        '-thoi_gian_dang')

    # Dữ liệu cho tab "Phê duyệt thành viên"
    pending_members = ThanhVienNhom.objects.filter(ma_nhom=nhom, trang_thai='ChoDuyet').select_related('ma_nguoi_dung')

    # Dữ liệu cho tab "Phê duyệt bài viết"
    pending_posts = BaiViet.objects.filter(ma_nhom=nhom, trang_thai='ChoDuyet').select_related('ma_nguoi_dung')

    # Dữ liệu cho tab "Thành viên của nhóm"
    members = ThanhVienNhom.objects.filter(ma_nhom=nhom, trang_thai='DuocDuyet').select_related('ma_nguoi_dung')

    context = {
        'nhom': nhom,
        'posts': posts,
        'pending_members': pending_members,
        'pending_posts': pending_posts,
        'members': members,
        'nguoi_dung': nguoi_dung
    }

    # Thay đổi đường dẫn template từ 'social/nhom_admin/nhom_detail.html' thành 'social/group_detail.html'
    return render(request, 'social/nhom_admin/group_detail.html', context)




def nhom_approve_members(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    nhom = get_object_or_404(Nhom, id=nhom_id)
    pending_members = ThanhVienNhom.objects.filter(ma_nhom=nhom, trang_thai='ChoDuyet').select_related('ma_nguoi_dung')

    context = {
        'nhom': nhom,
        'pending_members': pending_members,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/nhom_approve_members.html', context)
@login_required
def nhom_approve_posts(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    nhom = get_object_or_404(Nhom, id=nhom_id)
    pending_posts = BaiViet.objects.filter(ma_nhom=nhom, trang_thai='ChoDuyet').select_related('ma_nguoi_dung')

    context = {
        'nhom': nhom,
        'pending_posts': pending_posts,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/nhom_approve_posts.html', context)
@login_required
def nhom_members(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    nhom = get_object_or_404(Nhom, id=nhom_id)
    members = ThanhVienNhom.objects.filter(ma_nhom=nhom, trang_thai='DuocDuyet').select_related('ma_nguoi_dung')

    context = {
        'nhom': nhom,
        'members': members,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/nhom_members.html', context)
@login_required
@require_POST
def api_delete_group(request, nhom_id):
    try:

        nguoi_dung = request.user.nguoidung
        nhom = get_object_or_404(Nhom, id=nhom_id)

        # Kiểm tra quyền: chỉ Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa nhóm!'}, status=403)

        nhom.delete()
        return JsonResponse({'success': True, 'message': 'Nhóm đã được xóa thành công!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@require_POST
def api_approve_group(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
        if nguoi_dung.vai_tro != 'Admin':
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền!'}, status=403)

        nhom = get_object_or_404(Nhom, id=nhom_id, trang_thai='ChoDuyet')
        nhom.trang_thai = 'DaDuyet'
        nhom.save()
        return JsonResponse({'success': True, 'message': 'Nhóm đã được duyệt!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def api_reject_group(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
        if nguoi_dung.vai_tro != 'Admin':
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền!'}, status=403)

        nhom = get_object_or_404(Nhom, id=nhom_id, trang_thai='ChoDuyet')
        nhom.delete()
        return JsonResponse({'success': True, 'message': 'Nhóm đã bị từ chối!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@require_POST
def api_invite_members(request, nhom_id):
    return JsonResponse({'success': True, 'message': 'Đã gửi lời mời thành công.'})

@login_required
@require_POST
def api_approve_member(request, nhom_id, user_id):
    return JsonResponse({'success': True, 'message': 'Đã phê duyệt thành viên thành công.'})

@login_required
@require_POST
def api_reject_member(request, nhom_id, user_id):
    return JsonResponse({'success': True, 'message': 'Đã từ chối thành viên thành công.'})

@login_required
@require_POST
def api_remove_member(request, nhom_id, user_id):
    return JsonResponse({'success': True, 'message': 'Đã xóa thành viên thành công.'})

@login_required
@require_POST
def api_approve_post(request, nhom_id, post_id):
    return JsonResponse({'success': True, 'message': 'Đã phê duyệt bài viết thành công.'})

@login_required
@require_POST
def api_reject_post(request, nhom_id, post_id):
    return JsonResponse({'success': True, 'message': 'Đã từ chối bài viết thành công.'})

@login_required
@require_POST
def create_post(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng'}, status=400)

    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.ma_nguoi_dung = nguoi_dung
        post.trang_thai = 'DaDuyet'  # Bài công khai không cần duyệt
        post.post_type = request.POST.get('post_type', 'text')
        post.save()

        # Xử lý thăm dò ý kiến
        if post.post_type == 'poll':
            option_count = 0
            # Lấy các lựa chọn từ dữ liệu gửi lên (option_1, option_2, ...)
            for i in range(1, 11):  # Tối đa 10 lựa chọn
                option_text = request.POST.get(f'option_{i}')
                if option_text and option_text.strip():
                    PollOption.objects.create(bai_viet=post, text=option_text.strip())
                    option_count += 1
                if option_count >= 10:
                    break
            if option_count < 2:
                post.delete()
                return JsonResponse({'success': False, 'error': 'Thăm dò ý kiến cần ít nhất 2 lựa chọn'}, status=400)

        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'content': post.noi_dung,
            'post_type': post.post_type,
            'image_url': post.image.url if post.image else None,
            'video_url': post.video.url if post.video else None,
            'file_url': post.file.url if post.file else None,
        })
    else:
        return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)


# Bình luận
@login_required
@require_POST
def add_comment(request, post_id):
    try:
        post = BaiViet.objects.get(id=post_id)
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'success': False, 'error': 'Nội dung bình luận không được để trống'})
        comment = BinhLuan.objects.create(ma_nguoi_dung=request.user.nguoidung, ma_bai_viet=post, noi_dung=content)
        return JsonResponse({
            'success': True,
            'username': request.user.nguoidung.ho_ten,
            'content': comment.noi_dung,
            'created_at': comment.thoi_gian.strftime('%d/%m/%Y %H:%M')
        })

    except BaiViet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



@login_required
def get_comments(request, post_id):
    try:
        post = BaiViet.objects.get(id=post_id)
        comments = post.binh_luan.all().order_by('-thoi_gian')
        comments_data = [
            {
                'username': comment.ma_nguoi_dung.ho_ten,
                'content': comment.noi_dung,
                'created_at': comment.thoi_gian.strftime('%d/%m/%Y %H:%M')
            }
            for comment in comments
        ]
        return JsonResponse({'success': True, 'comments': comments_data})
    except BaiViet.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Tạo nhóm
@login_required
def create_group(request):
    if request.method == 'POST':
        ten_hoi_thoai = request.POST.get('ten_hoi_thoai')
        thanh_vien_ids = request.POST.getlist('thanh_vien')
        hoi_thoai = HoiThoai.objects.create(
            ten_hoi_thoai=ten_hoi_thoai,
            la_nhom=True
        )
        current_user = request.user.nguoidung
        hoi_thoai.thanh_vien.add(current_user)
        for user_id in thanh_vien_ids:
            hoi_thoai.thanh_vien.add(NguoiDung.objects.get(user__id=user_id))
        return redirect('message', hoi_thoai_id=hoi_thoai.id)

    nguoi_dung_list = NguoiDung.objects.exclude(user=request.user)
    return render(request, 'social/create_group.html', {'nguoi_dung_list': nguoi_dung_list})

# Đổi mật khẩu
from django.contrib.auth import update_session_auth_hash


@login_required
def change_password(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng.')
        return redirect('profile')  # Sửa lỗi chính tả

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu cũ không chính xác.')
            return render(request, 'social/profile.html', {
                'nguoi_dung': nguoi_dung,
                'show_change_password_modal': True
            })

        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới và xác nhận mật khẩu không khớp.')
            return render(request, 'social/profile.html', {
                'nguoi_dung': nguoi_dung,
                'show_change_password_modal': True
            })

        # Đổi mật khẩu
        request.user.set_password(new_password)
        request.user.save()

        # QUAN TRỌNG: Update session để không bị logout
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Đổi mật khẩu thành công!')
        return redirect('profile')

    return render(request, 'social/profile.html', {'nguoi_dung': nguoi_dung})


# Đặt lại mật khẩu

def reset_password_view(request):
    logger.debug("Bắt đầu quá trình đặt lại mật khẩu")
    if 'reset_email' not in request.session:
        logger.warning("Không tìm thấy reset_email trong session")
        messages.error(request, 'Không tìm thấy thông tin đặt lại mật khẩu. Vui lòng thử lại.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not new_password or not confirm_password:
            logger.warning("Trường mật khẩu trống")
            messages.error(request, 'Vui lòng nhập đầy đủ mật khẩu mới và xác nhận mật khẩu.')
            return render(request, 'social/login/reset_password.html')

        if new_password != confirm_password:
            logger.warning("Mật khẩu không khớp")
            messages.error(request, 'Mật khẩu mới và xác nhận mật khẩu không khớp.')
            return render(request, 'social/login/reset_password.html')

        try:
            nguoi_dung = NguoiDung.objects.get(email=request.session['reset_email'])
            user = nguoi_dung.user
            user.set_password(new_password)
            user.save()
            logger.info(f"Đặt lại mật khẩu thành công cho {request.session['reset_email']}")
            messages.success(request, 'Đặt lại mật khẩu thành công! Vui lòng đăng nhập.')
            del request.session['reset_email']
            return redirect('login')
        except NguoiDung.DoesNotExist:
            logger.warning(f"Không tìm thấy người dùng với email: {request.session['reset_email']}")
            messages.error(request, 'Không tìm thấy người dùng. Vui lòng thử lại.')
            return redirect('forgot_password')
        except Exception as e:
            logger.error(f"Lỗi không mong muốn khi đặt lại mật khẩu: {str(e)}")
            messages.error(request, f'Đã xảy ra lỗi: {str(e)}. Vui lòng thử lại.')
            return render(request, 'social/login/reset_password.html')

    return render(request, 'social/login/reset_password.html')

# Gửi lại OTP (đăng ký)
def resend_register_otp_view(request):
    logger.debug("Bắt đầu quá trình gửi lại OTP đăng ký")
    if 'register_email' not in request.session:
        logger.warning("Không tìm thấy register_email trong session")
        messages.error(request, 'Không tìm thấy thông tin đăng ký. Vui lòng đăng ký lại.')
        return redirect('register')

    email = request.session['register_email']
    otp_attempts = request.session.get('otp_attempts', 0)

    # Giới hạn số lần gửi lại OTP
    if otp_attempts >= 3:
        logger.warning(f"Đã đạt giới hạn gửi lại OTP cho {email}")
        messages.error(request, 'Bạn đã vượt quá số lần gửi lại OTP. Vui lòng thử lại sau.')
        del request.session['register_email']
        if 'pending_data' in request.session:
            del request.session['pending_data']
        del request.session['otp_attempts']
        if 'otp_verify_attempts' in request.session:
            del request.session['otp_verify_attempts']
        if 'initial_otp_attempts' in request.session:
            del request.session['initial_otp_attempts']
        return redirect('register')

    # Xóa OTP cũ
    PendingRegistration.objects.filter(email=email, is_verified=False).delete()
    logger.debug(f"Đã xóa OTP cũ cho {email}")

    # Tạo OTP mới
    pending_reg = PendingRegistration(
        email=email,
        password=request.session['pending_data']['password'],
        ho_ten=request.session['pending_data']['ho_ten'],
    )
    pending_reg.save()
    logger.debug(f"Đã tạo OTP mới cho {email}")

    # Gửi email OTP
    subject = 'Xác nhận đăng ký tài khoản DUE Social'
    message = f'Mã xác nhận mới của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Đã gửi lại OTP đến {email}: {pending_reg.otp_code}")
        request.session['otp_attempts'] = otp_attempts + 1
        messages.success(request, 'Đã gửi lại mã xác nhận. Vui lòng kiểm tra email của bạn.')
    except Exception as e:
        logger.error(f"Không thể gửi lại OTP đến {email}: {str(e)}")
        messages.error(request, 'Không thể gửi email. Vui lòng thử lại.')
        pending_reg.delete()
        if request.session['otp_attempts'] >= 3:
            logger.warning(f"Đạt giới hạn gửi lại OTP sau thất bại cho {email}")
            del request.session['register_email']
            if 'pending_data' in request.session:
                del request.session['pending_data']
            del request.session['otp_attempts']
            if 'otp_verify_attempts' in request.session:
                del request.session['otp_verify_attempts']
            if 'initial_otp_attempts' in request.session:
                del request.session['initial_otp_attempts']

    return redirect('verify_register_otp')

# Thêm view tìm kiếm nhóm cho admin của
@login_required
def search_groups_admin(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=400)

    if nguoi_dung.vai_tro != 'Admin':
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền truy cập!'}, status=403)

    query = request.GET.get('q', '').strip()
    logger.info(f"Tìm kiếm nhóm với từ khóa: {query}")

    try:
        groups = Nhom.objects.filter(
            ten_nhom__icontains=query
        ).select_related('nguoi_tao')
        logger.info(f"Tìm thấy {groups.count()} nhóm")
    except Exception as e:
        logger.error(f"Lỗi khi truy vấn nhóm: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Lỗi truy vấn dữ liệu: {str(e)}'}, status=500)

    # Trả về JSON cho AJAX
    groups_data = [
        {
            'id': group.id,
            'ten_nhom': group.ten_nhom,
            'avatar': group.avatar.url if group.avatar else None
        }
        for group in groups
    ]
    return JsonResponse({
        'success': True,
        'groups': groups_data
    })




# Cập nhật view `nhom_list` để hiển thị tất cả nhóm nếu có query parameter "all"
@login_required
def nhom_list(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    show_all_groups = request.GET.get('all', False)
    if show_all_groups:
        groups = Nhom.objects.filter(trang_thai='DaDuyet').select_related('nguoi_tao')
        context = {
            'groups': groups,
            'nguoi_dung': nguoi_dung,
            'show_all_groups': True,
        }
        return render(request, 'social/nhom_admin/all_groups.html', context)

    # Lấy tất cả bài viết của các nhóm đã duyệt
    posts = BaiViet.objects.filter(
        ma_nhom__isnull=False,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related('cam_xuc', 'binh_luan', 'poll_options',
                                                                  'poll_votes').order_by('-thoi_gian_dang')

    # Lấy danh sách nhóm chờ duyệt
    pending_groups = Nhom.objects.filter(trang_thai='ChoDuyet').select_related('nguoi_tao')

    # Lấy danh sách bài viết đã thích
    liked_posts = CamXuc.objects.filter(
        ma_nguoi_dung=nguoi_dung
    ).values_list('ma_bai_viet_id', flat=True)

    context = {
        'posts': posts,
        'pending_groups': pending_groups,
        'nguoi_dung': nguoi_dung,
        'liked_posts': liked_posts,
    }
    return render(request, 'social/nhom_admin/nhom_list.html', context)
# Tạo nhóm mới cho Admin
from django.views.decorators.csrf import ensure_csrf_cookie
@login_required
@ensure_csrf_cookie
def create_group_admin(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        logger.error("Không tìm thấy thông tin người dùng")
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=400)

    if nguoi_dung.vai_tro != 'Admin':
        logger.error(f"Người dùng {nguoi_dung.ho_ten} không có quyền Admin")
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền truy cập!'}, status=403)

    if request.method == 'POST':
        try:
            form = GroupForm(request.POST, request.FILES)
            if form.is_valid():
                nhom = form.save(commit=False)
                nhom.nguoi_tao = nguoi_dung
                nhom.trang_thai = 'DaDuyet'
                nhom.save()

                ThanhVienNhom.objects.create(
                    ma_nhom=nhom,
                    ma_nguoi_dung=nguoi_dung,
                    trang_thai='DuocDuyet',
                    la_quan_tri_vien=True
                )

                logger.info(f"Nhóm '{nhom.ten_nhom}' được tạo thành công bởi {nguoi_dung.ho_ten}")
                return JsonResponse({
                    'success': True,
                    'message': f'Nhóm "{nhom.ten_nhom}" đã được tạo thành công!',
                    'group_id': nhom.id
                })
            else:
                logger.warning(f"Lỗi xác thực form: {form.errors.as_json()}")
                return JsonResponse({
                    'success': False,
                    'message': 'Vui lòng kiểm tra lại thông tin nhập.',
                    'errors': form.errors.as_json()
                }, status=400)
        except Exception as e:
            logger.error(f"Lỗi khi tạo nhóm: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Đã xảy ra lỗi khi tạo nhóm: {str(e)}'
            }, status=500)
    else:
        form = GroupForm()
        context = {
            'form': form,
            'nguoi_dung': nguoi_dung
        }
        logger.info("Hiển thị form tạo nhóm")
        return render(request, 'social/nhom_admin/create_group.html', context)



# API xóa nhóm
# ... (các import khác giữ nguyên)
from django.db import transaction
from django.db.utils import IntegrityError

@login_required
@require_POST
def api_delete_group(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
        nhom = get_object_or_404(Nhom, id=nhom_id)

        # Kiểm tra quyền: Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            logger.error(f"Người dùng {nguoi_dung.ho_ten} không có quyền xóa nhóm {nhom.ten_nhom}")
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa nhóm này!'}, status=403)

        # Xóa nhóm trong một transaction
        with transaction.atomic():
            # Xóa các bản ghi liên quan đến BaiViet trước
            bai_viet_ids = BaiViet.objects.filter(ma_nhom=nhom).values_list('id', flat=True)
            PollOption.objects.filter(bai_viet__id__in=bai_viet_ids).delete()
            PollVote.objects.filter(bai_viet__id__in=bai_viet_ids).delete()
            CamXuc.objects.filter(ma_bai_viet__id__in=bai_viet_ids).delete()
            BinhLuan.objects.filter(ma_bai_viet__id__in=bai_viet_ids).delete()
            BaiViet.objects.filter(ma_nhom=nhom).delete()

            # Xóa các bản ghi liên quan đến Nhom
            ThanhVienNhom.objects.filter(ma_nhom=nhom).delete()
            LoiMoiNhom.objects.filter(ma_nhom=nhom).delete()

            # Xóa nhóm
            nhom.delete()

        logger.info(f"Nhóm {nhom.ten_nhom} đã được xóa bởi {nguoi_dung.ho_ten}")
        return JsonResponse({'success': True, 'message': 'Nhóm đã được xóa thành công!'})

    except Nhom.DoesNotExist:
        logger.error(f"Nhóm với ID {nhom_id} không tồn tại")
        return JsonResponse({'success': False, 'message': 'Nhóm không tồn tại!'}, status=404)
    except IntegrityError as e:
        logger.error(f"Lỗi ràng buộc khóa ngoại khi xóa nhóm ID {nhom_id}: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Không thể xóa nhóm do có dữ liệu liên quan!'}, status=400)
    except Exception as e:
        logger.error(f"Lỗi khi xóa nhóm ID {nhom_id}: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Có lỗi xảy ra khi xóa nhóm: {str(e)}'}, status=500)

from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NguoiDung
from .forms import LoginForm
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    logger.debug("Starting login process")
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            logger.debug(f"Attempting to authenticate user with email: {email}")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                if not user.is_active:
                    logger.warning(f"User {email} is inactive")
                    messages.error(request, 'Tài khoản của bạn đã bị vô hiệu hóa.')
                    return render(request, 'social/login/login.html', {'form': form})
                try:
                    auth_login(request, user, backend='social.authentication.TaiKhoanBackend')
                    logger.info(f"User {email} logged in successfully")
                    messages.success(request, 'Đăng nhập thành công!')
                    return redirect('home')
                except Exception as e:
                    logger.error(f"Failed to log in user {email}: {str(e)}")
                    messages.error(request, 'Đã xảy ra lỗi khi đăng nhập. Vui lòng thử lại.')
            else:
                # Kiểm tra lý do xác thực thất bại
                if not NguoiDung.objects.filter(email=email).exists():
                    logger.warning(f"Login failed: Email {email} does not exist")
                    messages.error(request, 'Email không tồn tại trong hệ thống.')
                else:
                    logger.warning(f"Login failed: Incorrect password for {email}")
                    messages.error(request, 'Mật khẩu không đúng.')
        else:
            logger.warning(f"Login form invalid: {form.errors}")
            messages.error(request, f'Vui lòng kiểm tra lại thông tin nhập: {form.errors}')
    else:
        form = LoginForm()
        logger.debug("Rendering login form")

    return render(request, 'social/login/login.html', {'form': form})

logger = logging.getLogger(__name__)


@login_required
def nhom_admin_main(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    # Lấy danh sách nhóm chờ duyệt
    try:
        pending_groups = Nhom.objects.filter(trang_thai='ChoDuyet').select_related('nguoi_tao')
        logger.info(f"Tìm thấy {pending_groups.count()} nhóm chờ duyệt")
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách nhóm chờ duyệt: {str(e)}")
        pending_groups = Nhom.objects.none()

    # Lấy danh sách tất cả các nhóm đã duyệt
    try:
        groups = Nhom.objects.filter(trang_thai='DaDuyet').select_related('nguoi_tao')
        logger.info(f"Tìm thấy {groups.count()} nhóm đã duyệt")
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách nhóm đã duyệt: {str(e)}")
        groups = Nhom.objects.none()

    # Lấy tất cả bài viết của các nhóm đã duyệt
    try:
        posts = BaiViet.objects.filter(
            ma_nhom__isnull=False,
            trang_thai='DaDuyet'
        ).select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related('cam_xuc', 'binh_luan', 'poll_options', 'poll_votes').order_by('-thoi_gian_dang')
        logger.info(f"Tìm thấy {posts.count()} bài viết của các nhóm đã duyệt")
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách bài viết: {str(e)}")
        posts = BaiViet.objects.none()

    # Lấy danh sách bài viết đã thích
    try:
        liked_posts = CamXuc.objects.filter(
            ma_nguoi_dung=nguoi_dung
        ).values_list('ma_bai_viet_id', flat=True)
        logger.info(f"Tìm thấy {liked_posts.count()} bài viết đã thích bởi người dùng {nguoi_dung.ho_ten}")
    except Exception as e:
        logger.error(f"Lỗi khi lấy danh sách bài viết đã thích: {str(e)}")
        liked_posts = []

    context = {
        'pending_groups': pending_groups,
        'groups': groups,
        'posts': posts,
        'nguoi_dung': nguoi_dung,
        'liked_posts': liked_posts,
    }
    logger.info("Render template 'social/nhom_admin/group_main.html'")
    return render(request, 'social/nhom_admin/group_main.html', context)

# Trang phê duyệt nhóm
@login_required
def nhom_admin_approval(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    # Lấy danh sách nhóm chờ duyệt
    pending_groups = Nhom.objects.filter(trang_thai='ChoDuyet').select_related('nguoi_tao')

    context = {
        'pending_groups': pending_groups,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/group_approval.html', context)


# Trang danh sách nhóm
@login_required
def nhom_admin_list(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    # Lấy danh sách tất cả các nhóm đã duyệt
    groups = Nhom.objects.filter(trang_thai='DaDuyet').select_related('nguoi_tao')

    context = {
        'groups': groups,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/nhom_admin/group_list.html', context)


# API phê duyệt nhóm
@login_required
@require_POST
def api_approve_group_admin(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
        if nguoi_dung.vai_tro != 'Admin':
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền!'}, status=403)

        nhom = get_object_or_404(Nhom, id=nhom_id, trang_thai='ChoDuyet')
        nhom.trang_thai = 'DaDuyet'
        nhom.save()
        return JsonResponse({'success': True, 'message': 'Nhóm đã được duyệt!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)



# API từ chối nhóm
@login_required
@require_POST
def api_reject_group_admin(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
        if nguoi_dung.vai_tro != 'Admin':
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền!'}, status=403)

        nhom = get_object_or_404(Nhom, id=nhom_id, trang_thai='ChoDuyet')
        nhom.delete()
        return JsonResponse({'success': True, 'message': 'Nhóm đã bị từ chối!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


# API phê duyệt yêu cầu thành viên
@login_required
@require_POST
def api_approve_member_request(request, request_id):
    try:
        nguoi_dung = request.user.nguoidung
        thanh_vien = get_object_or_404(ThanhVienNhom, id=request_id, trang_thai='ChoDuyet')
        nhom = thanh_vien.ma_nhom

        # Kiểm tra quyền: chỉ Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt thành viên!'}, status=403)

        thanh_vien.trang_thai = 'DuocDuyet'
        thanh_vien.save()
        return JsonResponse({'success': True, 'message': 'Thành viên đã được duyệt!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
# API từ chối yêu cầu thành viên
@login_required
@require_POST
def api_reject_member_request(request, request_id):
    try:
        nguoi_dung = request.user.nguoidung
        thanh_vien = get_object_or_404(ThanhVienNhom, id=request_id, trang_thai='ChoDuyet')
        nhom = thanh_vien.ma_nhom

        # Kiểm tra quyền: chỉ Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối thành viên!'}, status=403)

        thanh_vien.delete()
        return JsonResponse({'success': True, 'message': 'Yêu cầu thành viên đã bị từ chối!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# API phê duyệt bài viết
@login_required
@require_POST
def api_approve_post_request(request, post_id):
    try:
        nguoi_dung = request.user.nguoidung
        bai_viet = get_object_or_404(BaiViet, id=post_id, trang_thai='ChoDuyet')
        nhom = bai_viet.ma_nhom

        # Kiểm tra quyền: chỉ Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết!'}, status=403)

        bai_viet.trang_thai = 'DaDuyet'
        bai_viet.save()
        return JsonResponse({'success': True, 'message': 'Bài viết đã được duyệt!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# API từ chối bài viết
@login_required
@require_POST
def api_reject_post_request(request, post_id):
    try:
        nguoi_dung = request.user.nguoidung
        bai_viet = get_object_or_404(BaiViet, id=post_id, trang_thai='ChoDuyet')
        nhom = bai_viet.ma_nhom

        # Kiểm tra quyền: chỉ Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối bài viết!'}, status=403)

        bai_viet.delete()
        return JsonResponse({'success': True, 'message': 'Bài viết đã bị từ chối!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# API xóa thành viên khỏi nhóm
@login_required
@require_POST
def api_remove_member_from_group(request, member_id):
    try:
        nguoi_dung = request.user.nguoidung
        thanh_vien = get_object_or_404(ThanhVienNhom, id=member_id, trang_thai='DuocDuyet')
        nhom = thanh_vien.ma_nhom

        # Kiểm tra quyền: chỉ Admin hoặc quản trị viên nhóm
        is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            la_quan_tri_vien=True,
            trang_thai='DuocDuyet'
        ).exists()

        if not is_admin_or_moderator:
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa thành viên!'}, status=403)

        thanh_vien.delete()
        return JsonResponse({'success': True, 'message': 'Thành viên đã bị xóa khỏi nhóm!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

from django.shortcuts import render

def nhom_approve_groups(request):
    # Giả sử bạn có một model tên là Group và cần lấy danh sách nhóm đang chờ duyệt
    pending_groups = Group.objects.filter(status='pending')  # Điều chỉnh tùy theo model của bạn
    groups = Group.objects.filter(status='approved')  # Lấy danh sách nhóm đã duyệt cho sidebar
    context = {
        'pending_groups': pending_groups,
        'groups': groups,
    }
    return render(request, 'social/nhom_admin/group_approval.html', context)


# Trong file views.py
def phe_duyet_nhom(request):
    # Lấy danh sách các nhóm đang chờ phê duyệt
    nhom_cho_duyet = Nhom.objects.filter(trang_thai='cho_duyet')
    context = {
        'nhom_list': nhom_cho_duyet,
        'title': 'Phê duyệt nhóm'
    }
    return render(request, 'group_approval.html', context)

def tat_ca_nhom(request):
    # Lấy tất cả các nhóm
    tat_ca_nhom = Nhom.objects.all()
    context = {
        'nhom_list': tat_ca_nhom,
        'title': 'Tất cả nhóm'
    }
    return render(request, 'group_list.html', context)

#chi tiết nhóm
@login_required
def admin_group_detail(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    logger.info(f"Truy cập chi tiết nhóm ID: {nhom_id} bởi người dùng: {nguoi_dung.ho_ten}")

    try:
        nhom = get_object_or_404(Nhom, id=nhom_id)
        logger.info(f"Nhóm tìm thấy: {nhom.ten_nhom}")
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin nhóm ID {nhom_id}: {str(e)}")
        messages.error(request, 'Không tìm thấy nhóm!')
        return redirect('admin_group')

    # Vì đây là giao diện dành riêng cho Admin, đặt is_admin_or_moderator = True
    is_admin_or_moderator = True

    try:
        bai_viet_list = BaiViet.objects.filter(
            ma_nhom=nhom,
            trang_thai='DaDuyet'
        ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')
        logger.info(f"Tìm thấy {bai_viet_list.count()} bài viết đã duyệt")

        thanh_vien_cho_duyet = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            trang_thai='ChoDuyet'
        ).select_related('ma_nguoi_dung')
        logger.info(f"Tìm thấy {thanh_vien_cho_duyet.count()} thành viên chờ duyệt")

        bai_viet_cho_duyet = BaiViet.objects.filter(
            ma_nhom=nhom,
            trang_thai='ChoDuyet'
        ).select_related('ma_nguoi_dung')
        logger.info(f"Tìm thấy {bai_viet_cho_duyet.count()} bài viết chờ duyệt")

        thanh_vien_list = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            trang_thai='DuocDuyet'
        ).select_related('ma_nguoi_dung')
        logger.info(f"Tìm thấy {thanh_vien_list.count()} thành viên đã duyệt")

        nhom_list = Nhom.objects.filter(trang_thai='DaDuyet')
        logger.info(f"Tìm thấy {nhom_list.count()} nhóm đã duyệt")
    except Exception as e:
        logger.error(f"Lỗi khi truy vấn dữ liệu nhóm ID {nhom_id}: {str(e)}")
        messages.error(request, 'Có lỗi xảy ra khi tải dữ liệu nhóm!')
        return redirect('admin_group')

    context = {
        'nhom': nhom,
        'posts': bai_viet_list,
        'pending_members': thanh_vien_cho_duyet,
        'pending_posts': bai_viet_cho_duyet,
        'members': thanh_vien_list,
        'nguoi_dung': nguoi_dung,
        'groups': nhom_list,
        'is_admin_or_moderator': is_admin_or_moderator,
        'active_tab': request.GET.get('tab', 'feed')
    }

    logger.info(f"Render template 'social/nhom_admin/group_detail.html' cho nhóm ID: {nhom_id}")
    return render(request, 'social/nhom_admin/group_detail.html', context)
@login_required
def message_view(request, hoi_thoai_id=None):
    search_query = request.GET.get('search', '')
    # Lấy danh sách hội thoại không bị trùng lặp
    hoi_thoai_list = HoiThoai.objects.filter(thanh_vien=request.user.nguoidung).distinct().order_by(
        '-cap_nhat_thoi_gian')
    if search_query:
        hoi_thoai_list = hoi_thoai_list.filter(ten_hoi_thoai__icontains=search_query)

    selected_hoi_thoai = None
    tin_nhan_list = []
    if hoi_thoai_id:
        selected_hoi_thoai = get_object_or_404(HoiThoai, id=hoi_thoai_id, thanh_vien=request.user.nguoidung)
        tin_nhan_list = TinNhan.objects.filter(ma_hoi_thoai=selected_hoi_thoai).order_by('thoi_gian')

    if request.method == 'POST' and selected_hoi_thoai:
        form = TinNhanForm(request.POST)
        if form.is_valid():
            tin_nhan = form.save(commit=False)
            tin_nhan.ma_hoi_thoai = selected_hoi_thoai
            tin_nhan.ma_nguoi_dung = request.user.nguoidung
            tin_nhan.save()

            # Cập nhật thời gian của hội thoại để sắp xếp đúng
            selected_hoi_thoai.cap_nhat_thoi_gian = timezone.now()
            selected_hoi_thoai.save(update_fields=['cap_nhat_thoi_gian'])

            # Sử dụng HttpResponseRedirect để tránh việc gửi lại form khi refresh
            return HttpResponseRedirect(reverse('message', args=[selected_hoi_thoai.id]))
    else:
        form = TinNhanForm()

    context = {
        'hoi_thoai_list': hoi_thoai_list,
        'selected_hoi_thoai': selected_hoi_thoai,
        'tin_nhan_list': tin_nhan_list,
        'form': form,
    }
    return render(request, 'social/message.html', context)

@login_required
def add_member(request, hoi_thoai_id):
    if request.method == 'POST':
        hoi_thoai = get_object_or_404(HoiThoai, id=hoi_thoai_id, thanh_vien=request.user.nguoidung)
        if not hoi_thoai.la_nhom:
            messages.error(request, "Chỉ có thể thêm thành viên vào nhóm.")
            return redirect('message', hoi_thoai_id=hoi_thoai_id)

        member_email = request.POST.get('member-email').strip()
        try:
            new_member = NguoiDung.objects.get(email=member_email)
            if new_member not in hoi_thoai.thanh_vien.all():
                hoi_thoai.thanh_vien.add(new_member)
                hoi_thoai.save()
                messages.success(request, f"Đã thêm {member_email} vào nhóm.")
            else:
                messages.warning(request, f"{member_email} đã ở trong nhóm.")
        except NguoiDung.DoesNotExist:
            messages.error(request, f"Không tìm thấy người dùng với email {member_email}.")

        return redirect('message', hoi_thoai_id=hoi_thoai_id)

    return render(request, 'social/message.html')

@login_required
def start_conversation(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Phương thức không được phép'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if not user_id:
            print("Error: Missing user_id in request body")
            return JsonResponse({'success': False, 'error': 'Thiếu thông tin người dùng'}, status=400)

        other_user = get_object_or_404(NguoiDung, user__id=user_id)
        current_user = request.user.nguoidung

        print(f"Starting conversation between {current_user.email} (ID: {current_user.user.id}) and {other_user.email} (ID: {other_user.user.id})")

        hoi_thoai = HoiThoai.objects.filter(
            thanh_vien=current_user,
            la_nhom=False
        ).filter(thanh_vien=other_user).distinct()

        if hoi_thoai.exists():
            hoi_thoai = hoi_thoai.first()
            print(f"Found existing conversation: {hoi_thoai.id}")
            print(f"Conversation members: {[member.email for member in hoi_thoai.thanh_vien.all()]}")
        else:
            hoi_thoai = HoiThoai.objects.create(
                ten_hoi_thoai=other_user.ho_ten or other_user.email,
                la_nhom=False
            )
            hoi_thoai.thanh_vien.add(current_user, other_user)
            hoi_thoai.save()
            print(f"Created new conversation: {hoi_thoai.id} between {current_user.email} and {other_user.email}")
            print(f"Conversation members: {[member.email for member in hoi_thoai.thanh_vien.all()]}")

        members = hoi_thoai.thanh_vien.all()
        if current_user not in members or other_user not in members:
            print("Error: One or both users not in conversation members")
            hoi_thoai.thanh_vien.add(current_user, other_user)
            hoi_thoai.save()
            print(f"Fixed conversation members: {[member.email for member in hoi_thoai.thanh_vien.all()]}")

        # Thêm tin nhắn mặc định nếu không có tin nhắn
        if not TinNhan.objects.filter(ma_hoi_thoai=hoi_thoai).exists():
            TinNhan.objects.create(
                ma_hoi_thoai=hoi_thoai,
                ma_nguoi_dung=current_user,
                noi_dung="Bắt đầu trò chuyện",
                thoi_gian=timezone.now()
            )
            print(f"Added default message to conversation {hoi_thoai.id}")

        return JsonResponse({'success': True, 'hoi_thoai_id': hoi_thoai.id})
    except NguoiDung.DoesNotExist:
        print(f"User with ID {user_id} not found")
        return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại'}, status=404)
    except Exception as e:
        print(f"Error starting conversation: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def delete_conversation(request, hoi_thoai_id):
    """API để xóa một hội thoại và tất cả tin nhắn liên quan"""
    try:
        nguoi_dung = request.user.nguoidung
        hoi_thoai = get_object_or_404(HoiThoai, id=hoi_thoai_id)

        # Kiểm tra xem người dùng có phải thành viên của hội thoại không
        if not hoi_thoai.thanh_vien.filter(user=nguoi_dung.user).exists():
            return JsonResponse({'success': False, 'error': 'Bạn không có quyền xóa hội thoại này!'}, status=403)

        # Xóa tất cả tin nhắn liên quan trước
        TinNhan.objects.filter(ma_hoi_thoai=hoi_thoai).delete()

        # Xóa hội thoại
        hoi_thoai.delete()

        return JsonResponse({'success': True, 'message': 'Hội thoại đã được xóa thành công!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})

    # Sửa lỗi: Thêm tìm kiếm chính xác theo email
    if '@' in query:
        # Nếu query có chứa @, thực hiện tìm kiếm chính xác theo email
        users = NguoiDung.objects.filter(
            email__iexact=query
        ).exclude(user=request.user).select_related('user')[:10]
    else:
        # Tìm kiếm thông thường theo tên hoặc email chứa query
        users = NguoiDung.objects.filter(
            Q(ho_ten__icontains=query) | Q(email__icontains=query)
        ).exclude(user=request.user).select_related('user')[:10]

    users_data = [
        {
            'id': user.user.id,
            'ho_ten': user.ho_ten,
            'email': user.email,
            'avatar': user.avatar.url if user.avatar else None
        }
        for user in users
    ]
    return JsonResponse({'users': users_data}, safe=False)
@login_required
def search_usersmess(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})

    # Sửa lỗi: Thêm tìm kiếm chính xác theo email
    if '@' in query:
        # Nếu query có chứa @, thực hiện tìm kiếm chính xác theo email
        users = NguoiDung.objects.filter(
            email__iexact=query
        ).exclude(user=request.user).select_related('user')[:10]
    else:
        # Tìm kiếm thông thường theo tên hoặc email chứa query
        users = NguoiDung.objects.filter(
            Q(ho_ten__icontains=query) | Q(email__icontains=query)
        ).exclude(user=request.user).select_related('user')[:10]

    users_data = [
        {
            'id': user.user.id,
            'ho_ten': user.ho_ten,
            'email': user.email,
            'avatar': user.avatar.url if user.avatar else None
        }
        for user in users
    ]
    return JsonResponse({'users': users_data}, safe=False)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import HoiThoai, NguoiDung

@login_required
def create_groupmess(request):
    if request.method == 'POST':
        ten_hoi_thoai = request.POST.get('group-name')  # Match the form field name
        member_emails = request.POST.get('member-emails', '').split(',')  # Get comma-separated emails

        if not ten_hoi_thoai:
            messages.error(request, 'Vui lòng nhập tên nhóm!')
            return redirect('create_group')

        # Create the new group
        hoi_thoai = HoiThoai.objects.create(
            ten_hoi_thoai=ten_hoi_thoai,
            la_nhom=True,
            cap_nhat_thoi_gian=timezone.now()
        )

        # Add the current user as a member
        current_user = request.user.nguoidung
        hoi_thoai.thanh_vien.add(current_user)

        # Add selected members based on their emails
        for email in member_emails:
            email = email.strip()
            if email:  # Ensure the email is not empty
                try:
                    nguoi_dung = NguoiDung.objects.get(email=email)
                    if nguoi_dung != current_user:  # Avoid adding the current user again
                        hoi_thoai.thanh_vien.add(nguoi_dung)
                except NguoiDung.DoesNotExist:
                    messages.warning(request, f'Không tìm thấy người dùng với email {email}.')

        messages.success(request, f'Nhóm "{ten_hoi_thoai}" đã được tạo thành công!')
        return HttpResponseRedirect(reverse('message', args=[hoi_thoai.id]))

    # If not POST, render the form with a list of users (excluding the current user)
    nguoi_dung_list = NguoiDung.objects.exclude(user=request.user)
    return render(request, 'social/create_groupmess.html', {'nguoi_dung_list': nguoi_dung_list})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Nhom, ThanhVienNhom, BaiViet, CamXuc, PollVote, NguoiDung

@login_required
def group_view(request):
    try:
        nguoi_dung = request.user.nguoidung
        print(f"Accessing group_view, user: {request.user.email}, role: {nguoi_dung.vai_tro}")  # Log để gỡ lỗi
        if nguoi_dung.vai_tro == 'Admin':
            print("Redirecting Admin to admin_group")
            return redirect('admin_group')  # Chuyển hướng Admin
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    # Logic hiển thị trang nhóm cho sinh viên
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')

    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet',
        ma_nhom__trang_thai='DaDuyet'
    ).select_related('ma_nhom')

    group_ids = list(set(
        list(nhom_da_tham_gia.values_list('ma_nhom__id', flat=True)) +
        list(nhom_lam_qtrivien.values_list('ma_nhom__id', flat=True))
    ))

    all_group_posts = BaiViet.objects.filter(
        ma_nhom__id__in=group_ids,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related('poll_options', 'cam_xuc', 'binh_luan').order_by('-thoi_gian_dang')

    liked_posts = CamXuc.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        ma_bai_viet__in=all_group_posts
    ).values_list('ma_bai_viet__id', flat=True)

    poll_votes = PollVote.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        bai_viet__in=all_group_posts
    ).select_related('option')

    voted_options = {vote.option.id for vote in poll_votes}

    posts_with_details = []
    for post in all_group_posts:
        poll_options = post.poll_options.all()
        for option in poll_options:
            option.voted = option.id in voted_options
        posts_with_details.append({
            'post': post,
            'word_count': len(post.noi_dung.split()),
            'poll_options': poll_options
        })

    if not posts_with_details:
        messages.info(request, 'Hiện tại không có bài viết nào trong các nhóm của bạn.')

    context = {
        'all_group_posts': posts_with_details,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nguoi_dung': nguoi_dung,
        'liked_posts': list(liked_posts),
    }
    return render(request, 'social/group.html', context)

@login_required
def notif(request):
    """View hiển thị danh sách thông báo"""
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return render(request, 'social/notif.html', {'thong_bao_list': []})

    # Lấy tất cả thông báo của người dùng, sắp xếp theo thời gian mới nhất
    thong_bao_list = ThongBao.objects.filter(
        ma_nguoi_nhan=nguoi_dung
    ).select_related(
        'ma_nguoi_gui', 'ma_bai_viet', 'ma_nhom', 'ma_hoat_dong', 'ma_dat_lich'
    ).order_by('-thoi_gian')

    # Đánh dấu tất cả thông báo là đã đọc khi người dùng vào trang thông báo
    ThongBao.objects.filter(ma_nguoi_nhan=nguoi_dung, da_doc=False).update(da_doc=True)

    context = {
        'thong_bao_list': thong_bao_list,
        'nguoi_dung': nguoi_dung
    }
    return render(request, 'social/notif.html', context)


@login_required
def get_notification_count(request):
    """API để lấy số lượng thông báo chưa đọc"""
    try:
        nguoi_dung = request.user.nguoidung
        count = ThongBao.objects.filter(
            ma_nguoi_nhan=nguoi_dung,
            da_doc=False
        ).count()
        return JsonResponse({'count': count})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'count': 0})


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """API để đánh dấu thông báo đã đọc"""
    try:
        nguoi_dung = request.user.nguoidung
        notification = get_object_or_404(
            ThongBao,
            id=notification_id,
            ma_nguoi_nhan=nguoi_dung
        )
        notification.da_doc = True
        notification.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def mark_all_notifications_read(request):
    """API để đánh dấu tất cả thông báo đã đọc"""
    try:
        nguoi_dung = request.user.nguoidung
        ThongBao.objects.filter(
            ma_nguoi_nhan=nguoi_dung,
            da_doc=False
        ).update(da_doc=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_unread_messages_count(request):
    """API để lấy số lượng tin nhắn chưa đọc"""
    try:
        nguoi_dung = request.user.nguoidung
        hoi_thoai_list = HoiThoai.objects.filter(thanh_vien=nguoi_dung).distinct()

        unread_count = 0
        for hoi_thoai in hoi_thoai_list:
            # Đếm số tin nhắn mới hơn thời gian người dùng xem hội thoại
            last_message = hoi_thoai.tin_nhan.last()
            if last_message and last_message.ma_nguoi_dung != nguoi_dung:
                # Kiểm tra nếu tin nhắn cuối cùng không phải do người dùng gửi
                unread_count += 1

        return JsonResponse({'count': unread_count})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'count': 0})