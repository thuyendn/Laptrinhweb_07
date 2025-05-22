from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseRedirect
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


# View đăng bài viết
@login_required
@require_POST
def post_article(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})

    try:
        data = json.loads(request.body)
        group_id = int(data.get('group_id'))
        content = data.get('content')
        post_type = data.get('type')

        if not content:
            return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})

        nhom = Nhom.objects.get(id=group_id)

        # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
        membership = ThanhVienNhom.objects.filter(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            trang_thai='DuocDuyet'
        ).first()
        if not membership:
            return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})

        # Tạo bài viết mới
        bai_viet = BaiViet.objects.create(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            noi_dung=content,
            thoi_gian_dang=timezone.now(),
            trang_thai='ChoDuyet' if nhom.trang_thai_nhom == 'RiengTu' else 'DaDuyet'
        )

        response_data = {
            'success': True,
            'post_id': bai_viet.id,
            'ho_ten': nguoi_dung.ho_ten,
            'thoi_gian_dang': bai_viet.thoi_gian_dang.strftime('%d/%m/%Y %H:%M'),
            'type': post_type,
            'content': content
        }
        return JsonResponse(response_data)
    except Nhom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# View thích bài viết
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

# View thêm bình luận
@login_required
def them_binh_luan(request, ma_bai_viet):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'}, status=401)

    if request.method == 'POST':
        noi_dung = request.POST.get('noi_dung')
        try:
            nguoi_dung = request.user.nguoidung
            bai_viet = BaiViet.objects.get(id=ma_bai_viet)
            binh_luan = BinhLuan.objects.create(
                ma_bai_viet=bai_viet,
                ma_nguoi_dung=nguoi_dung,
                noi_dung=noi_dung,
                thoi_gian=timezone.now()
            )
            return JsonResponse({'success': True, 'ho_ten': nguoi_dung.ho_ten, 'noi_dung': noi_dung})
        except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist) as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

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
@login_required
def group_list(request):
    return render(request, 'social/group.html', {'show_modal': False})
@login_required
def tao_nhom_moi(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để tạo nhóm!')
        return redirect('login')

    if request.method == 'POST':
        ten_nhom = request.POST.get('group_name')
        mo_ta = request.POST.get('group_description')

        if ten_nhom:
            try:
                nguoi_dung = request.user.nguoidung
            except NguoiDung.DoesNotExist:
                messages.error(request, 'Không tìm thấy thông tin người dùng. Vui lòng cập nhật hồ sơ.')
                return redirect('group')

            # Tạo nhóm mới
            nhom = Nhom.objects.create(
                ten_nhom=ten_nhom,
                mo_ta=mo_ta,
                trang_thai='ChoDuyet',
                nguoi_tao=nguoi_dung
            )

            # Thêm người tạo làm quản trị viên
            ThanhVienNhom.objects.create(
                ma_nhom=nhom,
                ma_nguoi_dung=nguoi_dung,
                trang_thai='DuocDuyet',
                la_quan_tri_vien=True
            )

            messages.success(request, f'Nhóm "{ten_nhom}" đã được gửi yêu cầu tạo! Đang chờ duyệt.')
            return redirect('group')
        else:
            messages.error(request, 'Vui lòng nhập tên nhóm!')
            return redirect('group')

    return redirect('group')
@login_required
def search_groups(request):
    if not request.user.is_authenticated:
        return render(request, 'social/Nhom/error.html', {'message': 'Người dùng chưa đăng nhập!'})

    try:
        nguoi_dung = request.user.nguoidung
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
        trang_thai='DuocDuyet'
    ).values_list('ma_nhom', flat=True)
    joined_groups = all_groups.filter(id__in=joined_memberships)

    pending_memberships = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='ChoDuyet'
    ).values_list('ma_nhom', flat=True)
    pending_groups = all_groups.filter(id__in=pending_memberships)

    unjoined_groups = all_groups.exclude(id__in=joined_memberships).exclude(id__in=pending_memberships)

    context = {
        'nguoi_dung': nguoi_dung,
        'joined_groups': joined_groups,
        'pending_groups': pending_groups,
        'unjoined_groups': unjoined_groups,
        'search_query': search_query
    }
    return render(request, 'social/Nhom/group_search_results.html', context)
@login_required
@require_POST
def join_group(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Người dùng chưa đăng nhập!'})

    try:
        nguoi_dung = request.user.nguoidung
        group_id = int(json.loads(request.body).get('group_id'))
        nhom = Nhom.objects.get(id=group_id)

        existing_membership = ThanhVienNhom.objects.filter(ma_nhom=nhom, ma_nguoi_dung=nguoi_dung).first()
        if existing_membership:
            return JsonResponse({'success': False, 'error': 'Bạn đã gửi yêu cầu hoặc đã tham gia nhóm này!'})

        ThanhVienNhom.objects.create(
            ma_nhom=nhom,
            ma_nguoi_dung=nguoi_dung,
            trang_thai='ChoDuyet'
        )
        return JsonResponse({'success': True})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại!'})
    except Nhom.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# View cho trang chi tiết nhóm đã tham gia
@login_required
def chi_tiet_nhom_dathamgia(request, group_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem chi tiết nhóm!')
        return redirect('login')

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('group_feed')

    # Lấy thông tin nhóm
    nhom = get_object_or_404(Nhom, id=group_id)

    # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
    membership = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet'
    ).first()
    if not membership:
        messages.error(request, 'Bạn không có quyền xem nhóm này vì chưa là thành viên được duyệt!')
        return redirect('group_feed')

    # Lấy danh sách bài viết của nhóm
    posts = BaiViet.objects.filter(
        ma_nhom=nhom,
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
        'nhom': nhom,
        'posts_with_wordcount': posts_with_wordcount,
        'nguoi_dung': nguoi_dung,
    }
    return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html', context)

# View cho trang nhóm đã tham gia
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

    # Lấy danh sách nhóm mà người dùng đã tham gia
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet'
    ).select_related('ma_nhom')

    return render(request, 'social/Nhom/nhom_da_tham_gia.html', {
        'nhom_da_tham_gia': nhom_da_tham_gia,
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

    # Lấy danh sách nhóm mà người dùng làm quản trị viên
    nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).select_related('ma_nhom')

    # Lấy danh sách nhóm đã tham gia, loại bỏ các nhóm mà người dùng làm quản trị viên
    admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
    nhom_da_tham_gia = ThanhVienNhom.objects.filter(
        ma_nguoi_dung=nguoi_dung,
        trang_thai='DuocDuyet'
    ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')

    return render(request, 'social/Nhom/nhom_lam_qtrivien.html', {
        'nhom_lam_qtrivien': nhom_lam_qtrivien,
        'nhom_da_tham_gia': nhom_da_tham_gia,
        'nguoi_dung': nguoi_dung
    })
@login_required
def chi_tiet_nhom_quan_tri_vien(request, ma_nhom):

    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem chi tiết nhóm!')
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
        messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
        return redirect('nhom_lam_qtrivien')

    danh_sach_bai_viet = BaiViet.objects.filter(
        ma_nhom=nhom,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')

    danh_sach_bai_viet_chi_tiet = []
    for bai_viet in danh_sach_bai_viet:
        so_tu = len(bai_viet.noi_dung.strip().split())
        da_thich = CamXuc.objects.filter(ma_bai_viet=bai_viet, ma_nguoi_dung=nguoi_dung).exists()
        danh_sach_bai_viet_chi_tiet.append({
            'bai_viet': bai_viet,
            'so_tu': so_tu,
            'so_luot_thich': CamXuc.objects.filter(ma_bai_viet=bai_viet).count(),
            'da_thich': da_thich
        })

    danh_sach_ban_be = NguoiDung.objects.exclude(user=nguoi_dung.user).all()

    return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', {
        'nhom': nhom,
        'danh_sach_bai_viet_chi_tiet': danh_sach_bai_viet_chi_tiet,
        'nguoi_dung': nguoi_dung,
        'danh_sach_ban_be': danh_sach_ban_be
    })
@login_required
@require_POST
def gui_binh_luan(request, ma_bai_viet):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=401)

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=400)

    bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet)
    noi_dung = request.POST.get('content')

    if not noi_dung:
        return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống!'}, status=400)

    BinhLuan.objects.create(
        ma_bai_viet=bai_viet,
        ma_nguoi_dung=nguoi_dung,
        noi_dung=noi_dung,
        thoi_gian=timezone.now()
    )

    return JsonResponse({'success': True, 'message': 'Bình luận đã được gửi!'})
@login_required
@require_POST
def gui_moi(request, ma_nhom):
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

    du_lieu = json.loads(request.body)
    danh_sach_ma_ban_be = du_lieu.get('friend_ids', [])

    for ma_ban_be in danh_sach_ma_ban_be:
        try:
            ban_be = NguoiDung.objects.get(user__id=ma_ban_be)
            LoiMoiNhom.objects.update_or_create(
                ma_nhom=nhom,
                ma_nguoi_nhan=ban_be,
                defaults={'ma_nguoi_gui': nguoi_dung, 'trang_thai': 'ChoDuyet', 'thoi_gian_gui': timezone.now()}
            )
        except NguoiDung.DoesNotExist:
            continue

    return JsonResponse({'success': True, 'message': 'Lời mời đã được gửi!'})
@login_required
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
        'nhom': nhom,
        'pending_members': pending_members,
        'nguoi_dung': nguoi_dung
    })
@login_required
@require_POST
def duyet_thanh_vien_xac_nhan(request, ma_nhom, ma_thanh_vien):
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
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt thành viên!'}, status=403)

    thanh_vien_can_duyet = get_object_or_404(ThanhVienNhom, ma_nhom=nhom, id=ma_thanh_vien)
    thanh_vien_can_duyet.trang_thai = 'DuocDuyet'
    thanh_vien_can_duyet.save()

    return JsonResponse({'success': True, 'message': 'Thành viên đã được phê duyệt!'})
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
@login_required
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
@login_required
@require_POST
def duyet_bai_viet_xac_nhan(request, ma_nhom, ma_bai_viet):
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
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết!'}, status=403)

    bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet, ma_nhom=nhom)
    bai_viet.trang_thai = 'DaDuyet'
    bai_viet.save()

    return JsonResponse({'success': True, 'message': 'Bài viết đã được phê duyệt!'})
@login_required
@require_POST
def tu_choi_bai_viet(request, ma_nhom, ma_bai_viet):
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
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối bài viết!'}, status=403)

    bai_viet = get_object_or_404(BaiViet, id=ma_bai_viet, ma_nhom=nhom)
    bai_viet.delete()

    return JsonResponse({'success': True, 'message': 'Bài viết đã bị từ chối và xóa!'})
@login_required
def thanh_vien_nhom(request, ma_nhom):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn cần đăng nhập để xem thành viên nhóm!')
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
        messages.error(request, 'Bạn không có quyền xem thành viên nhóm!')
        return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)

    members = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='DuocDuyet'
    ).select_related('ma_nguoi_dung')

    return render(request, 'social/Nhom/thanh_vien_nhom.html', {
        'nhom': nhom,
        'members': members,
        'nguoi_dung': nguoi_dung
    })
@login_required
@require_POST
def xoa_thanh_vien(request, ma_nhom, ma_thanh_vien):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Người dùng chưa đăng nhập!'}, status=403)

    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng trong hệ thống!'}, status=403)

    nhom = get_object_or_404(Nhom, id=ma_nhom)
    thanh_vien = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).first()

    if not thanh_vien:
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa thành viên!'}, status=403)

    thanh_vien_can_xoa = get_object_or_404(ThanhVienNhom, id=ma_thanh_vien, ma_nhom=nhom)
    thanh_vien_can_xoa.delete()

    return JsonResponse({'success': True, 'message': 'Thành viên đã bị xóa khỏi nhóm!'})
@login_required
@require_GET
def search_users(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    users = NguoiDung.objects.filter(ho_ten__icontains=query).exclude(user=request.user).values('user__id', 'ho_ten')[:10]
    return JsonResponse(list(users), safe=False)

# View hồ sơ

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
@require_POST
def vote_poll(request, post_id, option_id):
    try:
        nguoi_dung = request.user.nguoidung
        post = BaiViet.objects.get(id=post_id, post_type='poll')
        option = PollOption.objects.get(id=option_id, bai_viet=post)

        # Không kiểm tra existing_vote để cho phép vote nhiều lựa chọn
        PollVote.objects.create(bai_viet=post, ma_nguoi_dung=nguoi_dung, option=option)
        option.votes += 1
        option.save()

        # Tính toán kết quả
        total_votes = post.poll_votes.count()
        votes = {str(opt.id): opt.votes for opt in post.poll_options.all()}

        # Đếm số lượng người vote (distinct users)
        unique_voters = post.poll_votes.values('ma_nguoi_dung').distinct().count()

        return JsonResponse({
            'success': True,
            'total_votes': total_votes,
            'unique_voters': unique_voters,
            'votes': votes
        })
    except (NguoiDung.DoesNotExist, BaiViet.DoesNotExist, PollOption.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@login_required
@require_GET
def get_voters(request, option_id):
    try:
        option = PollOption.objects.get(id=option_id)
        voters = PollVote.objects.filter(option=option).select_related('ma_nguoi_dung')
        voters_list = [vote.ma_nguoi_dung.ho_ten for vote in voters]
        return JsonResponse({'success': True, 'voters': voters_list})
    except PollOption.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lựa chọn không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Tìm kiếm
@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # Thêm tham số phân loại tìm kiếm
    users = []
    posts = []

    if query:
        if search_type in ['all', 'users']:
            # Tìm kiếm người dùng
            users = NguoiDung.objects.filter(
                Q(ho_ten__icontains=query) | Q(email__icontains=query)
            ).exclude(user=request.user).select_related('user')[:10]

        if search_type in ['all', 'posts']:
            # Tìm kiếm bài viết
            posts = BaiViet.objects.filter(
                Q(noi_dung__icontains=query) &
                Q(ma_nhom__isnull=True) &
                Q(trang_thai='DaDuyet')
            ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')[:10]

    context = {
        'query': query,
        'users': users,
        'posts': posts,
        'search_type': search_type,
    }
    return render(request, 'social/search.html', context)


# Nhắn tin
@login_required
def message_view(request, hoi_thoai_id=None):
    search_query = request.GET.get('search', '')
    hoi_thoai_list = HoiThoai.objects.filter(thanh_vien=request.user.nguoidung).order_by('-tin_nhan__thoi_gian')
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
            return redirect('message', hoi_thoai_id=selected_hoi_thoai.id)
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
def group(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        return render(request, 'social/Nhom/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})

    # Phân luồng dựa trên vai trò
    if nguoi_dung.vai_tro == 'Admin':
        return redirect('admin_group')

    # Lấy danh sách nhóm cho Sinh viên
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

    posts_with_wordcount = []
    for post in posts:
        word_count = len(post.noi_dung.strip().split())
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
    return render(request, 'social/Nhom/group.html', context)

# Thông báo
@login_required
def notif(request):
    thong_bao_list = ThongBao.objects.filter(ma_nguoi_nhan=request.user.nguoidung).order_by('-thoi_gian')
    return render(request, 'social/notif.html', {'thong_bao_list': thong_bao_list})

# Đăng nhập
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


# Đăng xuất
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')

# views.py

# Đăng ký
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
            from django.core.validators import EmailValidator
            from django.core.exceptions import ValidationError
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
                    messages.error(request, 'Email này đã được đăng ký, vui lòng kiểm tra và nhập email khác để được nhận mã OTP.')
                    return render(request, 'social/login/register.html', {'form': form})

                # Xóa các đăng ký tạm thời đã hết hạn
                PendingRegistration.objects.filter(
                    email=email,
                    expires_at__lt=timezone.now()
                ).delete()
                logger.debug(f"Deleted expired PendingRegistration for {email}")

                # Tạo đăng ký tạm thời (không lưu mật khẩu và họ tên vào đây)
                pending_reg = PendingRegistration(
                    email=email,
                )
                pending_reg.save()
                logger.debug(f"Created PendingRegistration for {email}")

            # Lưu thông tin tạm thời vào session
            request.session['pending_data'] = {
                'email': email,
                'password': password,
                'ho_ten': ho_ten,
            }

            # Khởi tạo số lần gửi OTP ban đầu nếu chưa có
            if 'initial_otp_attempts' not in request.session:
                request.session['initial_otp_attempts'] = 0

            # Giới hạn số lần gửi OTP ban đầu
            if request.session['initial_otp_attempts'] >= 3:
                logger.warning(f"Max initial OTP attempts reached for {email}")
                messages.error(request, 'Bạn đã vượt quá số lần gửi OTP. Vui lòng thử lại sau.')
                del request.session['initial_otp_attempts']
                return render(request, 'social/login/register.html', {'form': form})

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
                    del request.session['initial_otp_attempts']
                return render(request, 'social/login/register.html', {'form': form})
        else:
            logger.warning(f"Registration form invalid: {form.errors}")
            messages.error(request, f'Vui lòng kiểm tra lại thông tin nhập: {form.errors}')
    else:
        form = RegisterForm()
        logger.debug("Rendering registration form")

    return render(request, 'social/login/register.html', {'form': form})

from django.db import transaction


# Xác thực OTP (đăng ký)
def verify_register_otp_view(request):
    logger.debug("Starting OTP verification for registration")
    if 'register_email' not in request.session or 'pending_data' not in request.session:
        logger.warning("No register_email or pending_data in session")
        messages.error(request, 'Không tìm thấy thông tin đăng ký. Vui lòng đăng ký lại.')
        return redirect('register')

    # Khởi tạo số lần nhập OTP sai nếu chưa có
    if 'otp_verify_attempts' not in request.session:
        request.session['otp_verify_attempts'] = 0

    if request.method == 'POST':
        otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
        entered_otp = ''.join(otp_digits)
        logger.debug(f"Received OTP: {entered_otp}")

        try:
            pending_reg = PendingRegistration.objects.get(email=request.session['register_email'], is_verified=False)
            logger.debug(f"Found PendingRegistration for {pending_reg.email}")

            if not pending_reg.is_valid():
                logger.warning(f"OTP expired for {pending_reg.email}")
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng đăng ký lại.')
                pending_reg.delete()
                del request.session['register_email']
                del request.session['pending_data']
                if 'otp_attempts' in request.session:
                    del request.session['otp_attempts']
                if 'otp_verify_attempts' in request.session:
                    del request.session['otp_verify_attempts']
                if 'initial_otp_attempts' in request.session:
                    del request.session['initial_otp_attempts']
                return redirect('register')

            if pending_reg.otp_code != entered_otp:
                logger.warning(f"Invalid OTP for {pending_reg.email}: {entered_otp}")
                request.session['otp_verify_attempts'] += 1
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_register_otp.html')

            # Lấy thông tin từ session
            pending_data = request.session['pending_data']
            email = pending_data['email']
            password = pending_data['password']
            ho_ten = pending_data['ho_ten']

            # Sử dụng giao dịch nguyên tử để tạo User và NguoiDung
            with transaction.atomic():
                # Tạo User
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )
                if not user.is_active:
                    logger.warning(f"User created but inactive: {user.email}")
                    messages.error(request, 'Tài khoản được tạo nhưng không active. Vui lòng liên hệ admin.')
                    user.delete()
                    pending_reg.delete()
                    del request.session['register_email']
                    del request.session['pending_data']
                    if 'otp_attempts' in request.session:
                        del request.session['otp_attempts']
                    if 'otp_verify_attempts' in request.session:
                        del request.session['otp_verify_attempts']
                    if 'initial_otp_attempts' in request.session:
                        del request.session['initial_otp_attempts']
                    return redirect('register')
                logger.debug(f"Created User: {user.email}")

                # Tạo NguoiDung trực tiếp, gán ho_ten từ form
                nguoi_dung = NguoiDung.objects.create(
                    user=user,
                    ho_ten=ho_ten,  # Lấy ho_ten từ dữ liệu trong session (từ form)
                    email=email
                )
                nguoi_dung.save()  # Gọi save() để kích hoạt logic trong phương thức save của NguoiDung

            pending_reg.is_verified = True
            pending_reg.save()
            del request.session['register_email']
            del request.session['pending_data']
            if 'otp_attempts' in request.session:
                del request.session['otp_attempts']
            if 'otp_verify_attempts' in request.session:
                del request.session['otp_verify_attempts']
            if 'initial_otp_attempts' in request.session:
                del request.session['initial_otp_attempts']
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
            # Xóa User nếu đã tạo mà lỗi xảy ra
            if 'user' in locals():
                user.delete()
            return redirect('register')

    return render(request, 'social/login/verify_register_otp.html')


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
    logger.debug("Starting OTP verification for forgot password")
    if 'otp_email' not in request.session:
        logger.warning("No otp_email in session")
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_digits = [request.POST.get(f'otp{i}', '') for i in range(1, 5)]
        entered_otp = ''.join(otp_digits)
        logger.debug(f"Received OTP: {entered_otp}")

        try:
            otp = OTP.objects.get(email=request.session['otp_email'], is_used=False)
            logger.debug(f"Found OTP for {otp.email}")

            if not otp.is_valid():
                logger.warning(f"OTP expired for {otp.email}")
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng thử lại.')
                otp.delete()
                return redirect('forgot_password')

            if otp.otp_code != entered_otp:
                logger.warning(f"Invalid OTP for {otp.email}: {entered_otp}")
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_otp.html')

            otp.is_used = True
            otp.save()
            request.session['reset_email'] = request.session['otp_email']
            del request.session['otp_email']
            if 'otp_attempts' in request.session:
                del request.session['otp_attempts']
            logger.info(f"OTP verified for {otp.email}")
            messages.success(request, 'Xác thực OTP thành công! Vui lòng đặt lại mật khẩu.')
            return redirect('reset_password')

        except OTP.DoesNotExist:
            logger.warning("OTP not found or already used")
            messages.error(request, 'Không tìm thấy thông tin OTP hoặc đã hết hạn.')
            return redirect('forgot_password')
        except Exception as e:
            logger.error(f"Unexpected error during OTP verification: {str(e)}")
            messages.error(request, 'Đã xảy ra lỗi không mong muốn. Vui lòng thử lại.')
            return redirect('forgot_password')

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
                return redirect('admin_extracurr')
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
@login_required
def change_password(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng.')
        return redirect('login')

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu cũ không chính xác.')
            return render(request, 'social/profile.html', {'nguoi_dung': nguoi_dung})

        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới và xác nhận mật khẩu không khớp.')
            return render(request, 'social/profile.html', {'nguoi_dung': nguoi_dung})

        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Đổi mật khẩu thành công! Vui lòng đăng nhập lại.')
        return redirect('login')

    return render(request, 'social/profile.html', {'nguoi_dung': nguoi_dung})

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'users': []})

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
    return JsonResponse({'users': users_data})

@login_required
@require_POST
def start_conversation(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        other_user = NguoiDung.objects.get(user__id=user_id)

        # Lấy người dùng hiện tại
        current_user = request.user.nguoidung

        # Lấy tất cả hội thoại mà người dùng hiện tại tham gia
        hoi_thoai_list = HoiThoai.objects.filter(thanh_vien=current_user)

        # Tìm hội thoại hiện có chứa cả current_user và other_user
        hoi_thoai = None
        for hoi in hoi_thoai_list:
            thanh_vien = hoi.thanh_vien.all()
            if other_user in thanh_vien and len(thanh_vien) == 2 and not hoi.la_nhom:
                hoi_thoai = hoi
                break

        if hoi_thoai:
            hoi_thoai_id = hoi_thoai.id
        else:
            # Tạo hội thoại cá nhân mới nếu chưa tồn tại
            hoi_thoai = HoiThoai.objects.create(
                ten_hoi_thoai=other_user.ho_ten,
                la_nhom=False
            )
            hoi_thoai.thanh_vien.add(current_user)
            hoi_thoai.thanh_vien.add(other_user)
            hoi_thoai_id = hoi_thoai.id

            # Gửi thông báo cho người nhận
            ThongBao.objects.create(
                ma_nguoi_nhan=other_user,
                noi_dung=f"{current_user.ho_ten} đã bắt đầu một cuộc trò chuyện với bạn.",
                loai='TinNhan',
                thoi_gian=timezone.now()
            )

        return JsonResponse({'success': True, 'hoi_thoai_id': hoi_thoai_id})
    except NguoiDung.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



# Đặt lại mật khẩu
@login_required
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
        messages.error(request, f'Không thể gửi email: {str(e)}. Vui lòng thử lại.')
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


# social/views.py
# Thêm view tìm kiếm nhóm cho admin
@login_required
def search_groups_admin(request):
    try:
        nguoi_dung = request.user.nguoidung
    except NguoiDung.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin người dùng!')
        return redirect('login')

    if nguoi_dung.vai_tro != 'Admin':
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('group')

    query = request.GET.get('q', '').strip()
    groups = Nhom.objects.filter(
        Q(ten_nhom__icontains=query) | Q(mo_ta__icontains=query),
        trang_thai='DaDuyet'
    ).select_related('nguoi_tao')

    context = {
        'groups': groups,
        'query': query,
        'nguoi_dung': nguoi_dung,
    }
    return render(request, 'social/nhom_admin/group_search_results.html', context)


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
        return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=400)

    if nguoi_dung.vai_tro != 'Admin':
        return JsonResponse({'success': False, 'message': 'Bạn không có quyền truy cập!'}, status=403)

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            nhom = form.save(commit=False)
            nhom.nguoi_tao = nguoi_dung
            nhom.trang_thai = 'DaDuyet'  # Admin tạo nhóm không cần phê duyệt
            nhom.save()

            # Thêm Admin làm quản trị viên
            ThanhVienNhom.objects.create(
                ma_nhom=nhom,
                ma_nguoi_dung=nguoi_dung,
                trang_thai='DuocDuyet',
                la_quan_tri_vien=True
            )

            return JsonResponse({'success': True, 'message': f'Nhóm "{nhom.ten_nhom}" đã được tạo thành công!'})
        else:
            return JsonResponse({'success': False, 'message': 'Vui lòng kiểm tra lại thông tin nhập.', 'errors': form.errors.as_json()}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Phương thức không được hỗ trợ!'}, status=405)



# API xóa nhóm
@login_required
@require_POST
def api_delete_group(request, nhom_id):
    try:
        nguoi_dung = request.user.nguoidung
        if nguoi_dung.vai_tro != 'Admin':
            return JsonResponse({'success': False, 'message': 'Bạn không có quyền!'}, status=403)

        nhom = get_object_or_404(Nhom, id=nhom_id)
        nhom.delete()
        return JsonResponse({'success': True, 'message': 'Nhóm đã được xóa thành công!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

# Trang chính quản lý nhóm
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
    pending_groups = Nhom.objects.filter(trang_thai='ChoDuyet').select_related('nguoi_tao')

    # Lấy danh sách tất cả các nhóm đã duyệt
    groups = Nhom.objects.filter(trang_thai='DaDuyet').select_related('nguoi_tao')

    # Lấy tất cả bài viết của các nhóm đã duyệt
    posts = BaiViet.objects.filter(
        ma_nhom__isnull=False,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung', 'ma_nhom').prefetch_related('cam_xuc', 'binh_luan').order_by('-thoi_gian_dang')

    # Lấy danh sách bài viết đã thích
    liked_posts = CamXuc.objects.filter(
        ma_nguoi_dung=nguoi_dung
    ).values_list('ma_bai_viet_id', flat=True)

    context = {
        'pending_groups': pending_groups,
        'groups': groups,
        'posts': posts,
        'nguoi_dung': nguoi_dung,
        'liked_posts': liked_posts,
    }
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

    nhom = get_object_or_404(Nhom, id=nhom_id)

    # Kiểm tra xem người dùng có phải là Admin hoặc quản trị viên nhóm
    is_admin_or_moderator = nguoi_dung.vai_tro == 'Admin' or ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        ma_nguoi_dung=nguoi_dung,
        la_quan_tri_vien=True,
        trang_thai='DuocDuyet'
    ).exists()

    bai_viet_list = BaiViet.objects.filter(
        ma_nhom=nhom,
        trang_thai='DaDuyet'
    ).select_related('ma_nguoi_dung').order_by('-thoi_gian_dang')

    thanh_vien_cho_duyet = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='ChoDuyet'
    ).select_related('ma_nguoi_dung')

    bai_viet_cho_duyet = BaiViet.objects.filter(
        ma_nhom=nhom,
        trang_thai='ChoDuyet'
    ).select_related('ma_nguoi_dung')

    thanh_vien_list = ThanhVienNhom.objects.filter(
        ma_nhom=nhom,
        trang_thai='DuocDuyet'
    ).select_related('ma_nguoi_dung')

    nhom_list = Nhom.objects.filter(trang_thai='DaDuyet')

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

    return render(request, 'social/nhom_admin/group_detail.html', context)

