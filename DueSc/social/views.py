from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import datetime, timedelta
import json

from . import models
from .models import (
    Stadium, PendingSchedule, ConfirmedSchedule, Like, Comment, PollOption, ThongBao, TaiKhoan, Post,
    DKNgoaiKhoa, NguoiDung, HoatDongNgoaiKhoa, HoiThoai, TinNhan, OTP, PendingRegistration, Nhom, ThanhVienNhom,
    BaiViet, CamXuc, BinhLuan
)
from .forms import ExtracurricularForm, TinNhanForm, LoginForm

# View đăng bài viết
@require_POST
def post_article(request):
    try:
        # Sử dụng người dùng tranvanb
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng tranvanb không tồn tại!'})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})

    try:
        data = json.loads(request.body)
        group_id = int(data.get('group_id'))
        content = data.get('content')
        post_type = data.get('type')

        if not content:
            return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})

        nhom = Nhom.objects.get(ma_nhom=group_id)

        # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
        membership = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            trang_thai='Được duyệt'
        ).first()
        if not membership:
            return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})

        # Tạo bài viết mới
        bai_viet = BaiViet.objects.create(
            MaNhom=nhom,
            MaNguoiDung=nguoi_dung,
            NoiDung=content,
            ThoiGianDang=timezone.now(),
            TrangThai=True
        )

        response_data = {
            'success': True,
            'post_id': bai_viet.MaBaiViet,
            'ho_ten': nguoi_dung.ho_ten,
            'thoi_gian_dang': bai_viet.ThoiGianDang.strftime('%d/%m/%Y %H:%M'),
            'type': post_type,
            'content': content
        }

        # Xử lý các loại bài viết khác (video, hình ảnh, tệp, thăm dò ý kiến)
        if post_type == 'video':
            response_data['media_data'] = data.get('media_data')
            response_data['file_name'] = data.get('file_name')
        elif post_type == 'image':
            response_data['media_data'] = data.get('media_data')
            response_data['file_name'] = data.get('file_name')
        elif post_type == 'file':
            response_data['media_data'] = data.get('media_data')
            response_data['file_name'] = data.get('file_name')
        elif post_type == 'poll':
            response_data['options'] = data.get('options')
        return JsonResponse(response_data)
    except Nhom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
# View thích bài viết
def like_post(request, ma_bai_viet):
    try:
        # Sử dụng người dùng tranvanb
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
        bai_viet = BaiViet.objects.get(MaBaiViet=ma_bai_viet)
        cam_xuc, created = CamXuc.objects.get_or_create(
            MaBaiViet=bai_viet,
            MaNguoiDung=nguoi_dung,
            defaults={'LoaiCamXuc': 'Thích'}
        )
        if not created:
            cam_xuc.delete()
            bai_viet.SoLuongCamXuc = max(0, bai_viet.SoLuongCamXuc - 1)
            liked = False
        else:
            bai_viet.SoLuongCamXuc += 1
            liked = True
        bai_viet.save()
        return JsonResponse({
            'SoLuongCamXuc': bai_viet.SoLuongCamXuc,
            'liked': liked
        })
    except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist):
        return JsonResponse({'error': 'Invalid request'}, status=400)

# View thêm bình luận
def them_binh_luan(request, ma_bai_viet):
    if request.method == 'POST':
        noi_dung = request.POST.get('noi_dung')
        try:
            # Sử dụng người dùng tranvanb
            user = User.objects.get(username='tranvanb')
            nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
            bai_viet = BaiViet.objects.get(MaBaiViet=ma_bai_viet)
            binh_luan = BinhLuan.objects.create(
                MaBaiViet=bai_viet,
                MaNguoiDung=nguoi_dung,
                NoiDung=noi_dung
            )
            return JsonResponse({'success': True, 'ho_ten': nguoi_dung.ho_ten, 'noi_dung': noi_dung})
        except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist) as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

# View cho bảng tin nhóm
def group_feed(request):
    try:
        # Sử dụng người dùng tranvanb
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except (User.DoesNotExist, NguoiDung.DoesNotExist):
        nguoi_dung = None

    if nguoi_dung:
        thanh_vien_nhom = ThanhVienNhom.objects.filter(
            ma_nguoi_dung=nguoi_dung,
            trang_thai='Được duyệt'
        ).values_list('ma_nhom', flat=True)

        posts = BaiViet.objects.filter(
            MaNhom__in=thanh_vien_nhom,
            TrangThai=True
        ).select_related('MaNguoiDung', 'MaNhom').order_by('-ThoiGianDang')

        # Tạo danh sách bài viết với số từ
        posts_with_wordcount = []
        for post in posts:
            word_count = len(post.NoiDung.strip().split())
            posts_with_wordcount.append({
                'post': post,
                'word_count': word_count
            })
    else:
        posts_with_wordcount = []

    context = {
        'posts_with_wordcount': posts_with_wordcount,
        'nguoi_dung': nguoi_dung,
    }
    return render(request, 'social/group.html', context)


def group_list(request):
    return render(request, 'social/group.html', {'show_modal': False})





def tao_nhom_moi(request):
    if request.method == 'POST':
        ten_nhom = request.POST.get('group_name')
        mo_ta = request.POST.get('group_description')

        if ten_nhom:
            # Tạo nhóm mới
            nhom = Nhom.objects.create(
                ten_nhom=ten_nhom,
                trang_thai_nhom='Chờ duyệt'
            )

            # Lấy NguoiDung tương ứng với User hiện tại
            try:
                nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=request.user.id)
            except NguoiDung.DoesNotExist:
                messages.error(request, 'Không tìm thấy thông tin người dùng. Vui lòng cập nhật hồ sơ.')
                return redirect('group')

            # Thêm người tạo làm Quản trị viên
            ThanhVienNhom.objects.create(
                ma_nhom=nhom,
                ma_nguoi_dung=nguoi_dung,
                vai_tro='Quản trị viên',
                trang_thai='Được duyệt'
            )

            # Cập nhật số lượng thành viên
            nhom.so_luong_thanh_vien = 1
            nhom.save()

            messages.success(request, f'Nhóm "{ten_nhom}" đã được gửi yêu cầu tạo! Đang chờ duyệt.')
            return redirect('group')
        else:
            messages.error(request, 'Vui lòng nhập tên nhóm!')
            return redirect('group')

    return redirect('group')
def search_groups(request):
    try:
        user = User.objects.get(username='tranvanb')
    except User.DoesNotExist:
        return render(request, 'social/Nhom/error.html', {'message': 'Người dùng tranvanb không tồn tại!'})

    try:
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except NguoiDung.DoesNotExist:
        return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})

    joined_groups = []
    pending_groups = []
    unjoined_groups = []

    search_query = request.GET.get('search', '').lower()
    all_groups = Nhom.objects.filter(ten_nhom__icontains=search_query)

    if not all_groups.exists():
        return render(request, 'social/Nhom/group_search_results.html', {
            'nguoi_dung': nguoi_dung,
            'joined_groups': [],
            'pending_groups': [],
            'unjoined_groups': [],
            'search_query': search_query,
            'error_message': f'Không tìm thấy nhóm nào với từ khóa "{search_query}"'
        })

    joined_memberships = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Được duyệt'
    ).values_list('ma_nhom', flat=True)
    joined_groups = all_groups.filter(ma_nhom__in=joined_memberships)

    pending_memberships = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Chờ duyệt'
    ).values_list('ma_nhom', flat=True)
    pending_groups = all_groups.filter(ma_nhom__in=pending_memberships)

    unjoined_groups = all_groups.exclude(ma_nhom__in=joined_memberships).exclude(ma_nhom__in=pending_memberships)

    context = {
        'nguoi_dung': nguoi_dung,
        'joined_groups': joined_groups,
        'pending_groups': pending_groups,
        'unjoined_groups': unjoined_groups,
        'search_query': search_query
    }
    return render(request, 'social/Nhom/group_search_results.html', context)

@require_POST
def join_group(request):
    try:
        user = User.objects.get(username='tranvanb')
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng tranvanb không tồn tại!'})

    try:
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
        group_id = int(json.loads(request.body).get('group_id'))
        nhom = Nhom.objects.get(ma_nhom=group_id)

        existing_membership = ThanhVienNhom.objects.filter(ma_nhom=nhom, ma_nguoi_dung=nguoi_dung).first()
        if existing_membership:
            return JsonResponse({'success': False, 'error': 'Bạn đã gửi yêu cầu hoặc đã tham gia nhóm này!'})

        ThanhVienNhom.objects.create(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            vai_tro='Thành viên',
            trang_thai='Chờ duyệt'
        )
        return JsonResponse({'success': True})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại!'})
    except Nhom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# View cho trang chi tiết nhóm đã tham gia
def chi_tiet_nhom_dathamgia(request, group_id):
    try:
        # Sử dụng người dùng tranvanb
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except (User.DoesNotExist, NguoiDung.DoesNotExist):
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('group_feed')

    # Lấy thông tin nhóm
    nhom = get_object_or_404(Nhom, ma_nhom=group_id)

    # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
    membership = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Được duyệt'
    ).first()
    if not membership:
        messages.error(request, 'Bạn không có quyền xem nhóm này vì chưa là thành viên được duyệt!')
        return redirect('group_feed')

    # Lấy danh sách bài viết của nhóm
    posts = BaiViet.objects.filter(
        MaNhom=nhom,
        TrangThai=True
    ).select_related('MaNguoiDung', 'MaNhom').order_by('-ThoiGianDang')

    # Tạo danh sách bài viết với số từ, chỉ lấy các bài viết có MaBaiViet hợp lệ
    posts_with_wordcount = []
    for post in posts:
        if post.MaBaiViet and post.NoiDung:  # Kiểm tra MaBaiViet và NoiDung không rỗng
            word_count = len(post.NoiDung.strip().split())
            posts_with_wordcount.append({
                'post': post,
                'word_count': word_count
            })

    context = {
        'nhom': nhom,
        'posts_with_wordcount': posts_with_wordcount,
        'nguoi_dung': nguoi_dung,
    }
    return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html', context)
def group_view(request):
    # Giả lập người dùng (dùng NguoiDung đầu tiên trong cơ sở dữ liệu)
    nguoi_dung = NguoiDung.objects.first()  # Lấy người dùng đầu tiên để kiểm tra
    if not nguoi_dung:
        # Nếu không có người dùng nào, tạo một người dùng giả lập
        nguoi_dung = NguoiDung.objects.create(
            ho_ten="Người dùng thử nghiệm",
            gioi_tinh="Nam",
            ngay_sinh="2000-01-01",
            ma_tai_khoan=9999
        )

    # Lấy danh sách nhóm mà người dùng đã tham gia
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Được duyệt'
    ).select_related('ma_nhom')

    # Lấy danh sách bài viết (giả định bạn đã có logic này)
    posts_with_wordcount = []  # Thay bằng logic lấy bài viết nếu cần

    return render(request, 'social/group.html', {
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'posts_with_wordcount': posts_with_wordcount,
        'nguoi_dung': nguoi_dung
    })

# View cho trang nhóm đã tham gia
def nhom_da_tham_gia(request):
    try:
        # Sử dụng người dùng tranvanb
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except (User.DoesNotExist, NguoiDung.DoesNotExist):
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('group')

    # Lấy danh sách nhóm mà người dùng đã tham gia
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Được duyệt'
    ).select_related('ma_nhom')

    return render(request, 'social/Nhom/nhom_da_tham_gia.html', {
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nguoi_dung': nguoi_dung
    })
# View cho trang nhóm làm quản trị viên
def nhom_lam_qtrivien(request):
    try:
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except (User.DoesNotExist, NguoiDung.DoesNotExist):
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('group')

    # Lấy danh sách nhóm mà người dùng làm quản trị viên
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).select_related('ma_nhom')

    # Lấy danh sách nhóm đã tham gia, loại bỏ các nhóm mà người dùng làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Được duyệt'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    return render(request, 'social/Nhom/nhom_lam_qtrivien.html', {
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nguoi_dung': nguoi_dung
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Nhom, ThanhVienNhom, NguoiDung, BaiViet, BinhLuan
from django.contrib.auth.models import User
from django.utils import timezone
import json

def chi_tiet_nhom_quan_tri_vien(request, ma_nhom):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        messages.error(request, 'Người dùng tranvanb không tồn tại trong hệ thống!')
        return redirect('nhom_lam_qtrivien')
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
        return redirect('nhom_lam_qtrivien')

    danh_sach_bai_viet = BaiViet.objects.filter(
        MaNhom=nhom,
        TrangThai=True
    ).select_related('MaNguoiDung').order_by('-ThoiGianDang')

    danh_sach_bai_viet_chi_tiet = []
    for bai_viet in danh_sach_bai_viet:
        so_tu = len(bai_viet.noi_dung.strip().split())
        da_thich = False  # Không cần kiểm tra like vì không đăng nhập
        danh_sach_bai_viet_chi_tiet.append({
            'bai_viet': bai_viet,
            'so_tu': so_tu,
            'so_luot_thich': bai_viet.so_luong_cam_xuc,
            'da_thich': da_thich
        })

    danh_sach_ban_be = NguoiDung.objects.exclude(ma_nguoi_dung=nguoi_dung_tranvanb.ma_nguoi_dung).all()

    return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', {
        'nhom': nhom,
        'danh_sach_bai_viet_chi_tiet': danh_sach_bai_viet_chi_tiet,
        'nguoi_dung': nguoi_dung_tranvanb,
        'danh_sach_ban_be': danh_sach_ban_be
    })

@require_POST
def gui_binh_luan(request, ma_bai_viet):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=400)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=400)

    bai_viet = get_object_or_404(BaiViet, ma_bai_viet=ma_bai_viet)
    noi_dung = request.POST.get('content')

    if not noi_dung:
        return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống!'}, status=400)

    BinhLuan.objects.create(
        ma_bai_viet=bai_viet,
        ma_nguoi_dung=nguoi_dung_tranvanb,
        noi_dung=noi_dung,
        thoi_gian_dang=timezone.now()
    )

    return JsonResponse({'success': True, 'message': 'Bình luận đã được gửi!'})

@require_POST
def gui_moi(request, ma_nhom):
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=403)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=403)

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền mời thành viên!'}, status=403)

    du_lieu = json.loads(request.body)
    danh_sach_ma_ban_be = du_lieu.get('friend_ids', [])

    for ma_ban_be in danh_sach_ma_ban_be:
        try:
            ban_be = NguoiDung.objects.get(ma_nguoi_dung=ma_ban_be)
            ThanhVienNhom.objects.update_or_create(
                ma_nhom=nhom,
                ma_nguoi_dung=ban_be,
                defaults={'vai_tro': 'Thành viên', 'trang_thai': 'Chờ duyệt', 'thoi_gian_tham_gia': timezone.now()}
            )
        except NguoiDung.DoesNotExist:
            continue

    return JsonResponse({'success': True, 'message': 'Lời mời đã được gửi!'})

def duyet_thanh_vien(request, ma_nhom):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        messages.error(request, 'Người dùng tranvanb không tồn tại trong hệ thống!')
        return redirect('nhom_lam_qtrivien')
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền phê duyệt thành viên!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    pending_members = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='Chờ duyệt'
    ).select_related('ma_nguoi_dung')
    print("Pending members:", list(pending_members))  # Debug

    return render(request, 'social/Nhom/duyet_thanh_vien.html', {
        'nhom': nhom,
        'pending_members': pending_members,
        'nguoi_dung': nguoi_dung_tranvanb
    })

@require_POST
def duyet_thanh_vien_xac_nhan(request, ma_nhom, ma_thanh_vien):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=403)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=403)

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt thành viên!'}, status=403)

    thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, ma_nguoi_dung__ma_nguoi_dung=ma_thanh_vien)
    thanh_vien_can_duyet.trang_thai = 'Được duyệt'
    thanh_vien_can_duyet.save()

    nhom.so_luong_thanh_vien = ThanhVienNhom.objects.filter(ma_nhom=nhom, trang_thai='Được duyệt').count()
    nhom.save()

    return JsonResponse({'success': True, 'message': 'Thành viên đã được phê duyệt!'})

@require_POST
def tu_choi_thanh_vien(request, ma_nhom, ma_thanh_vien):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=403)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=403)

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối thành viên!'}, status=403)

    thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, ma_nguoi_dung__ma_nguoi_dung=ma_thanh_vien)
    thanh_vien_can_duyet.trang_thai = 'Từ chối'
    thanh_vien_can_duyet.save()

    return JsonResponse({'success': True, 'message': 'Yêu cầu tham gia đã bị từ chối!'})

def duyet_bai_viet(request, ma_nhom):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        messages.error(request, 'Người dùng tranvanb không tồn tại trong hệ thống!')
        return redirect('nhom_lam_qtrivien')
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền phê duyệt bài viết!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    danh_sach_bai_viet_cho_duyet = BaiViet.objects.filter(
        MaNhom=nhom,
        TrangThai=False
    ).select_related('ma_nguoi_dung')

    return render(request, 'social/Nhom/duyet_bai_viet.html', {
        'nhom': nhom,
        'danh_sach_bai_viet_cho_duyet': danh_sach_bai_viet_cho_duyet,
        'nguoi_dung': nguoi_dung_tranvanb
    })

@require_POST
def duyet_bai_viet_xac_nhan(request, ma_nhom, ma_bai_viet):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=403)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=403)

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết!'}, status=403)

    bai_viet = get_object_or_404(BaiViet, ma_bai_viet=ma_bai_viet, MaNhom=nhom)
    bai_viet.trang_thai = True
    bai_viet.save()

    return JsonResponse({'success': True, 'message': 'Bài viết đã được phê duyệt!'})

@require_POST
def tu_choi_bai_viet(request, ma_nhom, ma_bai_viet):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=403)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=403)

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối bài viết!'}, status=403)

    bai_viet = get_object_or_404(BaiViet, ma_bai_viet=ma_bai_viet, MaNhom=nhom)
    bai_viet.delete()

    return JsonResponse({'success': True, 'message': 'Bài viết đã bị từ chối và xóa!'})

def thanh_vien_nhom(request, ma_nhom):
    # Lấy người dùng tranvanb
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        messages.error(request, 'Người dùng tranvanb không tồn tại trong hệ thống!')
        return redirect('nhom_lam_qtrivien')
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!')
        return redirect('nhom_lam_qtrivien')

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        messages.error(request, 'Bạn không có quyền xem thành viên nhóm!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    members = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        vai_tro='Thành viên',
        trang_thai='Được duyệt'
    ).select_related('ma_nguoi_dung')
    print("Members:", list(members))  # Debug

    return render(request, 'social/Nhom/thanh_vien_nhom.html', {
        'nhom': nhom,
        'members': members,
        'nguoi_dung': nguoi_dung_tranvanb
    })

@require_POST
def xoa_thanh_vien(request, ma_nhom, ma_thanh_vien):
    try:
        tai_khoan_tranvanb = User.objects.get(username='tranvanb')
        nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Người dùng tranvanb không tồn tại trong hệ thống!'}, status=403)
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!'}, status=403)

    nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung_tranvanb,
        ma_nhom=nhom,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa thành viên!'}, status=403)

    thanh_vien_can_xoa = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, ma_nguoi_dung__ma_nguoi_dung=ma_thanh_vien)
    thanh_vien_can_xoa.delete()

    nhom.so_luong_thanh_vien = ThanhVienNhom.objects.filter(ma_nhom=nhom, trang_thai='Được duyệt').count()
    nhom.save()

    return JsonResponse({'success': True, 'message': 'Thành viên đã bị xóa khỏi nhóm!'})
@require_GET
def search_users(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    users = NguoiDung.objects.filter(ho_ten__icontains=query).exclude(ma_nguoi_dung=request.user.nguoidung.ma_nguoi_dung).values('ma_nguoi_dung', 'ho_ten')[:10]
    return JsonResponse(list(users), safe=False)













from django.contrib.auth.decorators import login_required

# View hồ sơ
@login_required
def profile(request):
    try:
        tai_khoan = TaiKhoan.objects.get(user=request.user)
    except TaiKhoan.DoesNotExist:
        messages.error(request, 'Không tìm thấy tài khoản của bạn.')
        return redirect('login')
    return render(request, 'social/profile.html', {'tai_khoan': tai_khoan})


# Trang chủ
def home(request):
    if request.user.is_authenticated:
        try:
            tai_khoan = TaiKhoan.objects.get(user=request.user)
        except TaiKhoan.DoesNotExist:
            messages.error(request, 'Không tìm thấy tài khoản của bạn.')
            return redirect('login')

        ThongBao.objects.get_or_create(
            NguoiNhan=tai_khoan,
            NoiDung="Thông tin báo đăng mới.",
            defaults={'ThoiGian': timezone.now()}
        )
        ThongBao.objects.get_or_create(
            NguoiNhan=tai_khoan,
            NoiDung="Lịch đặt sân của bạn đã được duyệt.",
            defaults={'ThoiGian': timezone.now() - timezone.timedelta(days=2)}
        )
        posts = Post.objects.all().order_by('-created_at')
        liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        context = {
            'posts': posts,
            'liked_posts': liked_posts,
        }
    else:
        context = {}
    return render(request, 'social/home.html', context)


# Tìm kiếm
def search(request):
    return render(request, 'social/search.html')


# Nhắn tin
@login_required
def message_view(request, hoi_thoai_id=None):
    search_query = request.GET.get('search', '')
    hoi_thoai_list = HoiThoai.objects.filter(ThanhVien__user=request.user).order_by('-tin_nhan__ThoiGian')
    if search_query:
        hoi_thoai_list = hoi_thoai_list.filter(TenHoiThoai__icontains=search_query)

    selected_hoi_thoai = None
    tin_nhan_list = []
    if hoi_thoai_id:
        selected_hoi_thoai = get_object_or_404(HoiThoai, MaHoiThoai=hoi_thoai_id, ThanhVien__user=request.user)
        tin_nhan_list = TinNhan.objects.filter(MaHoiThoai=selected_hoi_thoai).order_by('ThoiGian')

    if request.method == 'POST' and selected_hoi_thoai:
        form = TinNhanForm(request.POST)
        if form.is_valid():
            tin_nhan = form.save(commit=False)
            tin_nhan.MaHoiThoai = selected_hoi_thoai
            tin_nhan.MaNguoiGui = TaiKhoan.objects.get(user=request.user)
            tin_nhan.save()
            return redirect('message', hoi_thoai_id=selected_hoi_thoai.MaHoiThoai)  # Sửa dòng này
    else:
        form = TinNhanForm()

    context = {
        'hoi_thoai_list': hoi_thoai_list,
        'selected_hoi_thoai': selected_hoi_thoai,
        'tin_nhan_list': tin_nhan_list,
        'form': form,
    }
    return render(request, 'social/message.html', context)

def group(request):
    try:
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except (User.DoesNotExist, NguoiDung.DoesNotExist):
        return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})

    # Lấy danh sách nhóm mà người dùng làm quản trị viên
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        vai_tro='Quản trị viên',
        trang_thai='Được duyệt'
    ).select_related('ma_nhom')

    # Lấy danh sách nhóm đã tham gia, loại bỏ các nhóm mà người dùng làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='Được duyệt'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    # Lấy danh sách bài viết từ các nhóm đã tham gia
    posts = BaiViet.objects.filter(
        MaNhom__in=nhom_da_tham_gia.values('ma_nhom'),
        TrangThai=True
    ).select_related('MaNguoiDung', 'MaNhom').order_by('-ThoiGianDang')

    # Tạo danh sách bài viết với số từ
    posts_with_wordcount = []
    for post in posts:
        word_count = len(post.NoiDung.strip().split())
        posts_with_wordcount.append({
            'post': post,
            'word_count': word_count
        })

    context = {
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'posts_with_wordcount': posts_with_wordcount,
        'nguoi_dung': nguoi_dung,
        'show_modal': False
    }
    return render(request, 'social/group.html', context)


# Lịch đặt sân
def schedule(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/dat_lich/schedule.html', {'stadiums': stadiums})


# Thông báo
@login_required
def notif(request):
    thong_bao_list = ThongBao.objects.filter(NguoiNhan__user=request.user).order_by('-ThoiGian')
    return render(request, 'social/notif.html', {'thong_bao_list': thong_bao_list})


# Thêm
def more(request):
    return render(request, 'social/more.html')


# Đăng nhập
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user, backend='social.authentication.TaiKhoanBackend')
                return redirect('home')
            else:
                messages.error(request, 'Email hoặc mật khẩu không đúng.')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin nhập.')
    else:
        form = LoginForm()

    return render(request, 'social/login/login.html', {'form': form})


# Đăng xuất
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')


# Đăng ký
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        ho_ten = request.POST.get('ho_ten')

        if not all([email, password, confirm_password, ho_ten]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return render(request, 'social/login/register.html')

        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
            return render(request, 'social/login/register.html')

        if TaiKhoan.objects.filter(Email=email).exists():
            messages.error(request, 'Email đã được sử dụng.')
            return render(request, 'social/login/register.html')

        PendingRegistration.objects.filter(email=email).delete()

        pending_reg = PendingRegistration.objects.create(
            email=email,
            password=password,
            ho_ten=ho_ten
        )

        subject = 'Xác nhận đăng ký tài khoản DUE Social'
        message = f'Mã xác nhận của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            request.session['register_email'] = email
            messages.success(request, 'Mã OTP đã được gửi đến email của bạn.')
            return redirect('verify_register_otp')
        except Exception as e:
            messages.error(request, f'Không thể gửi email: {str(e)}')
            pending_reg.delete()
            return render(request, 'social/login/register.html')

    return render(request, 'social/login/register.html')


# Quên mật khẩu
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not TaiKhoan.objects.filter(Email=email).exists():
            messages.error(request, 'Email không tồn tại trong hệ thống.')
            return render(request, 'social/login/forgot_password.html')

        otp_code = ''.join(random.choices(string.digits, k=4))
        otp = OTP.objects.create(
            email=email,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        subject = 'Đặt lại mật khẩu DUE Social'
        message = f'Mã xác nhận của bạn là: {otp_code}. Mã này có hiệu lực trong 10 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            request.session['forgot_email'] = email
            messages.success(request, 'Mã OTP đã được gửi đến email của bạn.')
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f'Không thể gửi email: {str(e)}')
            otp.delete()
            return render(request, 'social/login/forgot_password.html')

    return render(request, 'social/login/forgot_password.html')


# Xác thực OTP (quên mật khẩu)
def verify_otp_view(request):
    if request.method == 'POST':
        otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
        entered_otp = ''.join(otp_digits)

        try:
            otp = OTP.objects.get(email=request.session.get('forgot_email'), is_used=False)

            if not otp.is_valid():
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng thử lại.')
                otp.delete()
                return redirect('forgot_password')

            if otp.otp_code != entered_otp:
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_otp.html')

            otp.is_used = True
            otp.save()
            request.session['reset_email'] = request.session['forgot_email']
            del request.session['forgot_email']
            messages.success(request, 'Xác thực OTP thành công! Vui lòng đặt lại mật khẩu.')
            return redirect('reset_password')

        except OTP.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin OTP hoặc đã hết hạn.')
            return redirect('forgot_password')

    return render(request, 'social/login/verify_otp.html')


# Đặt lại mật khẩu
def reset_password_view(request):
    if 'reset_email' not in request.session:
        return redirect('forgot_password')

    email = request.session['reset_email']

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
            return render(request, 'social/login/reset_password.html')

        try:
            tai_khoan = TaiKhoan.objects.get(Email=email)
            tai_khoan.MatKhau = make_password(new_password)
            tai_khoan.save()

            del request.session['reset_email']
            messages.success(request, 'Đặt lại mật khẩu thành công! Vui lòng đăng nhập.')
            return redirect('login')
        except TaiKhoan.DoesNotExist:
            messages.error(request, 'Không tìm thấy tài khoản.')

    return render(request, 'social/login/reset_password.html')


# Xác thực OTP (đăng ký)
def verify_register_otp_view(request):
    if 'register_email' not in request.session:
        messages.error(request, 'Không tìm thấy thông tin đăng ký. Vui lòng đăng ký lại.')
        return redirect('register')

    if request.method == 'POST':
        otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
        entered_otp = ''.join(otp_digits)

        try:
            pending_reg = PendingRegistration.objects.get(email=request.session['register_email'], is_verified=False)

            if not pending_reg.is_valid():
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng đăng ký lại.')
                pending_reg.delete()
                del request.session['register_email']
                return redirect('register')

            if pending_reg.otp_code != entered_otp:
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_register_otp.html')

            # Tạo User trước
            user = User.objects.create_user(
                username=pending_reg.email,
                email=pending_reg.email,
                password=pending_reg.password
            )

            # Tạo NguoiDung và TaiKhoan
            nguoi_dung = NguoiDung.objects.create(ho_ten=pending_reg.ho_ten)
            tai_khoan = TaiKhoan.objects.create(
                Email=pending_reg.email,
                MatKhau=pending_reg.password,
                MaNguoiDung=nguoi_dung,
                user=user
            )
            nguoi_dung.ma_tai_khoan = tai_khoan.MaTaiKhoan
            nguoi_dung.save()

            pending_reg.is_verified = True
            pending_reg.save()
            del request.session['register_email']
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login')

        except PendingRegistration.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')
            return redirect('register')

    return render(request, 'social/login/verify_register_otp.html')


# Gửi lại mã OTP (đăng ký)
def resend_register_otp_view(request):
    if 'register_email' not in request.session:
        return redirect('register')

    email = request.session['register_email']

    try:
        pending_reg = PendingRegistration.objects.get(email=email, is_verified=False)
        pending_reg.otp_code = ''.join(random.choices(string.digits, k=4))
        pending_reg.expires_at = timezone.now() + timedelta(minutes=30)
        pending_reg.save()

        subject = 'Mã xác nhận đăng ký tài khoản DUE Social'
        message = f'Mã xác nhận mới của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
        messages.success(request, 'Đã gửi lại mã xác nhận. Vui lòng kiểm tra email của bạn.')
    except PendingRegistration.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')

    return redirect('verify_register_otp')


# Lịch đặt sân
def calendar_view(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        location = request.POST.get('location')
        name = request.user.MaNguoiDung.ho_ten if request.user.is_authenticated else request.POST.get('name', 'Unknown')
        email = request.user.email if request.user.is_authenticated else request.POST.get('email', 'unknown@example.com')
        student_id = request.POST.get('student_id', '')

        if selected_date and selected_time and location:
            try:
                try:
                    stadium = Stadium.objects.get(name=location)
                    standardized_location = stadium.name
                except Stadium.DoesNotExist:
                    standardized_location = "Sân bóng Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE)" if 'sân bóng' in location.lower() else "Nhà Đa năng Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE)" if 'nhà đa năng' in location.lower() else location

                date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                time_obj = datetime.strptime(selected_time, '%H:%M').time()
                pending = PendingSchedule(
                    name=name,
                    email=email,
                    date=date,
                    time=time_obj,
                    location=standardized_location,
                    student_id=student_id,
                    status='pending'
                )
                pending.save()
                messages.success(request, 'Lịch của bạn đã được gửi để chờ duyệt.')
                return redirect('calendar_view')
            except ValueError as e:
                messages.error(request, f'Lỗi định dạng ngày giờ: {e}')
            except Exception as e:
                messages.error(request, f'Lỗi khi lưu lịch: {e}')
        else:
            messages.error(request, 'Vui lòng chọn thời gian và địa điểm trước khi đặt lịch.')
        return redirect('calendar_view')

    location = request.GET.get('location', 'Sân bóng Trường Đại học Kinh tế - Đại học Đà Nẵng (DUE)')
    days = [
        {"name": "Sun", "date": 9},
        {"name": "Mon", "date": 10},
        {"name": "Tue", "date": 11},
        {"name": "Wed", "date": 12},
        {"name": "Thu", "date": 13},
        {"name": "Fri", "date": 14},
        {"name": "Sat", "date": 15},
    ]
    times = ["17:00", "18:00", "19:00", "20:00"]
    bookings = [
        {"date": datetime(2025, 3, 13).date(), "time": "18:00", "is_canceled": False},
        {"date": datetime(2025, 3, 14).date(), "time": "18:00", "is_canceled": True},
    ]

    context = {
        'days': days,
        'times': times,
        'bookings': bookings,
        'location': location,
    }
    print("Context data:", context)  # Thêm logging
    return render(request, 'social/dat_lich/calendar.html', context)

@login_required
def pending_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    pending_schedules = PendingSchedule.objects.filter(status='pending')
    context = {
        'pendings': pending_schedules,
    }
    return render(request, 'social/admin/admin_Schedule/choduyet.html', context)


@login_required
def Choduyet(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    location = request.GET.get('location', None)
    if not location:
        messages.error(request, 'Không tìm thấy địa điểm.')
        return redirect('admin_schedule')

    pendings = PendingSchedule.objects.filter(location=location, status='pending')
    context = {
        'pendings': pendings,
        'location': location,
    }
    return render(request, 'social/admin/admin_Schedule/Choduyet.html', context)


@login_required
def Xacnhan(request, pending_id):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    try:
        pending = PendingSchedule.objects.get(id=pending_id, status='pending')
        ConfirmedSchedule.objects.create(
            student_id=pending.student_id,
            name=pending.name,
            email=pending.email,
            date=pending.date,
            time=pending.time,
            location=pending.location,
            status='confirmed'
        )
        pending.delete()
        messages.success(request, 'Lịch đã được xác nhận thành công.')
    except PendingSchedule.DoesNotExist:
        messages.error(request, 'Lịch không tồn tại hoặc đã được xử lý.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def Huy(request, pending_id):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    try:
        pending = PendingSchedule.objects.get(id=pending_id, status='pending')
        pending.status = 'canceled'
        pending.save()
        messages.success(request, 'Lịch đã được hủy thành công.')
    except PendingSchedule.DoesNotExist:
        messages.error(request, 'Lịch không tồn tại hoặc đã được xử lý.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def HuyXemdanhsach(request, schedule_id):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    schedule = get_object_or_404(ConfirmedSchedule, id=schedule_id)
    schedule.status = "canceled"
    schedule.save()
    messages.success(request, "Lịch đã được hủy thành công.")
    return redirect('Xemdanhsach')


def admin_schedule(request):
    stadiums = Stadium.objects.all()
    context = {
        'stadiums': stadiums,
    }
    return render(request, 'social/admin/admin_Schedule/admin_schedule.html', context)


def stadium_list(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/dat_lich/schedule.html', {'stadiums': stadiums})


def Xemdanhsach(request):
    confirmed_schedules = ConfirmedSchedule.objects.all()
    return render(request, 'social/admin/admin_Schedule/Xemdanhsach.html', {'confirmed_schedules': confirmed_schedules})


# Sinh viên ngoại khóa
def phan_loai_nk_SV(nguoi_dung):
    now = timezone.now()
    se_tham_gia_ids = DKNgoaiKhoa.objects.filter(
        ma_sv=nguoi_dung,
        trang_thai=DKNgoaiKhoa.TrangThai.KHONG_THAM_GIA,
        ma_hd_nk__thoi_gian__gt=now
    ).values_list('ma_hd_nk_id', flat=True)
    da_tham_gia_ids = DKNgoaiKhoa.objects.filter(
        ma_sv=nguoi_dung,
        trang_thai=DKNgoaiKhoa.TrangThai.DA_THAM_GIA,
        ma_hd_nk__thoi_gian__lte=now
    ).values_list('ma_hd_nk_id', flat=True)
    se_tham_gia = HoatDongNgoaiKhoa.objects.filter(pk__in=se_tham_gia_ids)
    da_tham_gia = HoatDongNgoaiKhoa.objects.filter(pk__in=da_tham_gia_ids)
    return se_tham_gia, da_tham_gia


def extracurricular(request):
    nguoi_dung = NguoiDung.objects.get(ma_nguoi_dung=1)
    if request.method == "POST":
        ma_nk = request.POST.get("ma_nk")
        try:
            hoat_dong = HoatDongNgoaiKhoa.objects.get(ma_nk=ma_nk)
            _, created = DKNgoaiKhoa.objects.get_or_create(
                ma_hd_nk=hoat_dong,
                ma_sv=nguoi_dung,
                defaults={'trang_thai': DKNgoaiKhoa.TrangThai.KHONG_THAM_GIA}
            )
            if created:
                messages.success(request, "Bạn đã đăng ký tham gia thành công!")
            else:
                messages.info(request, "Bạn đã đăng ký hoạt động này rồi.")
        except HoatDongNgoaiKhoa.DoesNotExist:
            messages.error(request, "Hoạt động không tồn tại.")

    activities = HoatDongNgoaiKhoa.objects.all().order_by('-ma_nk')
    se_tham_gia, da_tham_gia = phan_loai_nk_SV(nguoi_dung)
    return render(request, 'social/extracurricular.html', {
        'activities': activities,
        'se_tham_gia': se_tham_gia,
        'da_tham_gia': da_tham_gia,
    })


def extracurricular_detail(request, pk):
    nguoi_dung = NguoiDung.objects.get(ma_nguoi_dung=1)
    activity = get_object_or_404(HoatDongNgoaiKhoa, pk=pk)
    se_tham_gia, da_tham_gia = phan_loai_nk_SV(nguoi_dung)
    return render(request, 'social/extracurricular_detail.html', {
        'activity': activity,
        'se_tham_gia': se_tham_gia,
        'da_tham_gia': da_tham_gia,
    })


# Admin ngoại khóa
def duyet_tat_ca_SV(request, activity):
    danh_sach_sv = request.POST.getlist('sinh_vien_duyet')
    if danh_sach_sv:
        DKNgoaiKhoa.objects.filter(
            id__in=danh_sach_sv,
            ma_hd_nk=activity
        ).update(trang_thai='DA_THAM_GIA')
        return len(danh_sach_sv)
    return 0


def duyet_tung_sinh_vien(request, activity, sinh_vien_id):
    try:
        dknk = DKNgoaiKhoa.objects.get(id=sinh_vien_id, ma_hd_nk=activity)
        dknk.trang_thai = DKNgoaiKhoa.TrangThai.DA_THAM_GIA
        dknk.save()
        messages.success(request, f"Đã xác nhận tham gia cho sinh viên {dknk.ma_sv.ho_ten}")
    except DKNgoaiKhoa.DoesNotExist:
        messages.error(request, "Không tìm thấy đăng ký sinh viên.")


def process_extracurricular_form(request, form_class, nguoi_dung):
    form = form_class(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.nguoi_dung = nguoi_dung
        instance.save()
        return True, form
    return False, form


def phan_loai_nk_GV():
    now = timezone.now()
    chua_dien_ra = HoatDongNgoaiKhoa.objects.filter(thoi_gian__gt=now).order_by('thoi_gian')
    da_dien_ra = HoatDongNgoaiKhoa.objects.filter(thoi_gian__lte=now).order_by('-thoi_gian')
    return chua_dien_ra, da_dien_ra


def admin_extracurr(request):
    request.user.nguoidung = NguoiDung.objects.get(ma_nguoi_dung=2)
    if request.method == 'POST':
        success, form = process_extracurricular_form(request, ExtracurricularForm, request.user.nguoidung)
        if success:
            return redirect('admin_extracurr')
    else:
        form = ExtracurricularForm()

    chua_dien_ra, da_dien_ra = phan_loai_nk_GV()
    activities = HoatDongNgoaiKhoa.objects.order_by('-ma_nk')
    return render(request, 'social/admin/admin_extracurr/admin_extracurr.html', {
        'form': form,
        'activities': activities,
        'chua_dien_ra': chua_dien_ra,
        'da_dien_ra': da_dien_ra
    })


def admin_extracurr_detail(request, pk):
    activity = get_object_or_404(HoatDongNgoaiKhoa, pk=pk)
    request.user.nguoidung = NguoiDung.objects.get(ma_nguoi_dung=2)
    sinh_vien_dang_ky = DKNgoaiKhoa.objects.filter(ma_hd_nk=activity)
    sinh_vien_list = []
    for dk in sinh_vien_dang_ky:
        sinh_vien = {
            'ho_ten': dk.ma_sv.ho_ten,
            'ma_tai_khoan': dk.ma_sv.ma_tai_khoan,
            'ma_nguoi_dung': dk.ma_sv.ma_nguoi_dung,
            'trang_thai': dk.trang_thai,
            'ngoaikhoa_id': dk.id
        }
        sinh_vien_list.append(sinh_vien)

    so_luong_dk = sinh_vien_dang_ky.count()
    so_luong_da_tham_gia = sinh_vien_dang_ky.filter(trang_thai='DA_THAM_GIA').count()

    if request.method == 'POST':
        if 'duyet_sinh_vien' in request.POST:
            sinh_vien_id = request.POST.get('sinh_vien_id')
            duyet_tung_sinh_vien(request, activity, sinh_vien_id)
            return redirect('admin_extracurr_detail', pk=pk)

        if 'duyet_all' in request.POST:
            so_duyet = duyet_tat_ca_SV(request, activity)
            messages.success(request, f"Đã duyệt {so_duyet} sinh viên.")
            return redirect('admin_extracurr_detail', pk=pk)
        else:
            success, form = process_extracurricular_form(request, ExtracurricularForm, request.user.nguoidung)
            if success:
                return redirect('admin_extracurr')
    else:
        form = ExtracurricularForm()

    chua_dien_ra, da_dien_ra = phan_loai_nk_GV()
    trang_thai_hoat_dong = 'chua_dien_ra' if activity in chua_dien_ra else (
        'da_dien_ra' if activity in da_dien_ra else 'khac')

    return render(request, 'social/admin/admin_extracurr/admin_extracurr_detail.html', {
        'activity': activity,
        'sinh_vien_list': sinh_vien_list,
        'trang_thai_hoat_dong': trang_thai_hoat_dong,
        'so_luong_dk': so_luong_dk,
        'so_luong_da_tham_gia': so_luong_da_tham_gia,
        'chua_dien_ra': chua_dien_ra,
        'da_dien_ra': da_dien_ra,
        'form': form
    })


def admin_group(request):
    return render(request, 'social/admin/admin_group.html')


# Nhóm admin
@login_required
def nhom_list(request):
    context = {}
    return render(request, 'social/nhom_admin/nhom_list.html', context)


@login_required
def nhom_detail(request, nhom_id):
    context = {}
    return render(request, 'social/nhom_admin/nhom_detail.html', context)


@login_required
def nhom_approve_members(request, nhom_id):
    context = {}
    return render(request, 'social/nhom_admin/nhom_approve_members.html', context)


@login_required
def nhom_approve_posts(request, nhom_id):
    context = {}
    return render(request, 'social/nhom_admin/nhom_approve_posts.html', context)


@login_required
def nhom_members(request, nhom_id):
    context = {}
    return render(request, 'social/nhom_admin/nhom_members.html', context)


@login_required
@require_POST
def api_delete_group(request, nhom_id):
    return JsonResponse({'success': True, 'message': 'Nhóm đã được xóa thành công.'})


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


# Tạo bài viết
@login_required
@require_POST
def create_post(request):
    try:
        content = request.POST.get('content')
        post_type = request.POST.get('post_type', 'text')

        if not content and post_type == 'text':
            return JsonResponse({'success': False, 'error': 'Nội dung không được để trống'})

        post = Post.objects.create(
            user=request.user,
            content=content,
            post_type=post_type
        )

        if post_type == 'image' and 'image' in request.FILES:
            post.image = request.FILES['image']
        elif post_type == 'video' and 'video' in request.FILES:
            post.video = request.FILES['video']
        elif post_type == 'file' and 'file' in request.FILES:
            post.file = request.FILES['file']
        elif post_type == 'poll':
            options = [request.POST.get(f'option_{i}') for i in range(1, 11) if request.POST.get(f'option_{i}')]
            if len(options) < 2:
                post.delete()
                return JsonResponse({'success': False, 'error': 'Thăm dò ý kiến cần ít nhất 2 lựa chọn'})
            for option_text in options:
                PollOption.objects.create(post=post, text=option_text)

        post.save()
        return JsonResponse({'success': True, 'post_id': post.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Thích bài viết
@login_required
@require_POST
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            liked = False
            count = post.likes.count()
        else:
            liked = True
            count = post.likes.count()
        return JsonResponse({'success': True, 'liked': liked, 'count': count})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Bình luận
@login_required
@require_POST
def add_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'success': False, 'error': 'Nội dung bình luận không được để trống'})
        comment = Comment.objects.create(user=request.user, post=post, content=content)
        return JsonResponse({
            'success': True,
            'username': request.user.MaNguoiDung.ho_ten,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
        })
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_comments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        comments = post.comments.all().order_by('-created_at')
        comments_data = [
            {
                'username': comment.user.MaNguoiDung.ho_ten,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
            }
            for comment in comments
        ]
        return JsonResponse({'success': True, 'comments': comments_data})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bài viết không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Bỏ phiếu
@login_required
@require_POST
def vote_poll(request, post_id, option_id):
    try:
        post = Post.objects.get(id=post_id)
        if post.post_type != 'poll':
            return JsonResponse({'success': False, 'error': 'Bài viết không phải là khảo sát'})
        option = PollOption.objects.get(id=option_id, post=post)
        option.votes += 1
        option.save()
        total_votes = sum(opt.votes for opt in post.poll_options.all())
        votes_data = {opt.id: opt.votes for opt in post.poll_options.all()}
        return JsonResponse({'success': True, 'total_votes': total_votes, 'votes': votes_data})
    except (Post.DoesNotExist, PollOption.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Lựa chọn không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# Tạo nhóm
@login_required
def create_group(request):
    if request.method == 'POST':
        ten_hoi_thoai = request.POST.get('ten_hoi_thoai')
        thanh_vien_ids = request.POST.getlist('thanh_vien')
        hoi_thoai = HoiThoai.objects.create(
            TenHoiThoai=ten_hoi_thoai,
            LoaiHoiThoai='Nhóm'
        )
        current_user = TaiKhoan.objects.get(user=request.user)
        hoi_thoai.ThanhVien.add(current_user)
        for ma_tai_khoan in thanh_vien_ids:
            hoi_thoai.ThanhVien.add(TaiKhoan.objects.get(MaTaiKhoan=ma_tai_khoan))
        return redirect('message', hoi_thoai_id=hoi_thoai.MaHoiThoai)  # Sửa dòng này

    tai_khoan_list = TaiKhoan.objects.exclude(user=request.user)
    return render(request, 'social/create_group.html', {'tai_khoan_list': tai_khoan_list})

# Đổi mật khẩu
@login_required
def change_password(request):
    try:
        tai_khoan = TaiKhoan.objects.get(user=request.user)
    except TaiKhoan.DoesNotExist:
        messages.error(request, 'Không tìm thấy tài khoản của bạn.')
        return redirect('login')

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not check_password(old_password, tai_khoan.MatKhau):
            messages.error(request, 'Mật khẩu cũ không chính xác.')
            return render(request, 'social/profile.html', {'tai_khoan': tai_khoan})  # Xóa show_change_password_modal

        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới và xác nhận mật khẩu không khớp.')
            return render(request, 'social/profile.html', {'tai_khoan': tai_khoan})  # Xóa show_change_password_modal

        tai_khoan.MatKhau = make_password(new_password)
        tai_khoan.save()
        messages.success(request, 'Đổi mật khẩu thành công! Vui lòng đăng nhập lại.')
        if 'user_id' in request.session:
            del request.session['user_id']
        return redirect('login')

    return render(request, 'social/profile.html', {'tai_khoan': tai_khoan})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})

    users = TaiKhoan.objects.filter(
        Q(MaNguoiDung__ho_ten__icontains=query) | Q(Email__icontains=query)
    ).exclude(user=request.user).select_related('MaNguoiDung')[:10]

    users_data = [
        {
            'id': user.MaTaiKhoan,
            'ho_ten': user.MaNguoiDung.ho_ten,
            'email': user.Email,
            'avatar': user.MaNguoiDung.avatar.url if hasattr(user.MaNguoiDung, 'avatar') and user.MaNguoiDung.avatar else None
        }
        for user in users
    ]
    return JsonResponse({'users': users_data})

@login_required
@require_POST
def start_conversation(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        other_user = TaiKhoan.objects.get(MaTaiKhoan=user_id)

        # Lấy danh sách hội thoại cá nhân của người dùng hiện tại
        current_user = TaiKhoan.objects.get(user=request.user)
        hoi_thoai_list = HoiThoai.objects.filter(
            LoaiHoiThoai='Cá nhân',
            ThanhVien=current_user
        )

        # Kiểm tra xem có hội thoại nào giữa hai người dùng không
        hoi_thoai = None
        for hoi in hoi_thoai_list:
            thanh_vien = hoi.ThanhVien.all()
            if len(thanh_vien) == 2 and other_user in thanh_vien:
                hoi_thoai = hoi
                break

        if hoi_thoai:
            hoi_thoai_id = hoi_thoai.MaHoiThoai
        else:
            # Tạo hội thoại cá nhân mới nếu chưa tồn tại
            hoi_thoai = HoiThoai.objects.create(
                TenHoiThoai=other_user.MaNguoiDung.ho_ten,
                LoaiHoiThoai='Cá nhân'
            )
            hoi_thoai.ThanhVien.add(current_user)
            hoi_thoai.ThanhVien.add(other_user)
            hoi_thoai_id = hoi_thoai.MaHoiThoai

            # Gửi thông báo cho người nhận
            ThongBao.objects.create(
                NguoiNhan=other_user,
                NoiDung=f"{current_user.MaNguoiDung.ho_ten} đã bắt đầu một cuộc trò chuyện với bạn.",
                ThoiGian=timezone.now()
            )

        return JsonResponse({'success': True, 'hoi_thoai_id': hoi_thoai_id})
    except TaiKhoan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})

    users = TaiKhoan.objects.filter(
        models.Q(MaNguoiDung__ho_ten__icontains=query) | models.Q(Email__icontains=query)
    ).exclude(user=request.user).select_related('MaNguoiDung')[:10]

    users_data = [
        {
            'id': user.MaTaiKhoan,
            'ho_ten': user.MaNguoiDung.ho_ten,
            'email': user.Email,
            'avatar': user.MaNguoiDung.avatar.url if user.MaNguoiDung.avatar else None
        }
        for user in users
    ]
    return JsonResponse({'users': users_data})




from django.views.decorators.http import require_POST
from django.db.models import Q

@login_required
@require_POST
def start_conversation(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        other_user = TaiKhoan.objects.get(MaTaiKhoan=user_id)

        # Lấy người dùng hiện tại
        current_user = TaiKhoan.objects.get(user=request.user)

        # Lấy tất cả hội thoại mà người dùng hiện tại tham gia (cả cá nhân và nhóm)
        hoi_thoai_list = HoiThoai.objects.filter(ThanhVien=current_user)

        # Tìm hội thoại hiện có (cá nhân hoặc nhóm) chứa cả current_user và other_user
        hoi_thoai = None
        for hoi in hoi_thoai_list:
            thanh_vien = hoi.ThanhVien.all()
            if other_user in thanh_vien:
                # Hội thoại này chứa cả current_user và other_user
                hoi_thoai = hoi
                break

        if hoi_thoai:
            # Nếu tìm thấy hội thoại (cá nhân hoặc nhóm), sử dụng hội thoại đó
            hoi_thoai_id = hoi_thoai.MaHoiThoai
            print(f"Using existing conversation: {hoi_thoai_id} ({hoi_thoai.LoaiHoiThoai})")
        else:
            # Nếu không tìm thấy hội thoại, tạo hội thoại cá nhân mới
            hoi_thoai = HoiThoai.objects.create(
                TenHoiThoai=other_user.MaNguoiDung.ho_ten,
                LoaiHoiThoai='Cá nhân'
            )
            hoi_thoai.ThanhVien.add(current_user)
            hoi_thoai.ThanhVien.add(other_user)
            hoi_thoai_id = hoi_thoai.MaHoiThoai
            print(f"Created new conversation: {hoi_thoai_id}")

            # Gửi thông báo cho người nhận
            ThongBao.objects.create(
                NguoiNhan=other_user,
                NoiDung=f"{current_user.MaNguoiDung.ho_ten} đã bắt đầu một cuộc trò chuyện với bạn.",
                ThoiGian=timezone.now()
            )

        return JsonResponse({'success': True, 'hoi_thoai_id': hoi_thoai_id})
    except TaiKhoan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})