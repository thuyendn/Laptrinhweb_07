from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Nhom, ThanhVienNhom, NguoiDung
from django.contrib.auth.models import User
from .models import Stadium, PendingSchedule
from .models import CamXuc, BaiViet, NguoiDung
from .models import BaiViet, BinhLuan, NguoiDung
from .models import Nhom, ThanhVienNhom, NguoiDung
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Nhom, ThanhVienNhom, NguoiDung
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
from django.http import JsonResponse


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

# @require_POST
# def post_article(request, group_id):
#     try:
#         user = request.user
#         nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
#     except User.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Người dùng không tồn tại!'})
#     except NguoiDung.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Không tìm thấy thông tin người dùng!'})
#
#     try:
#         nhom = Nhom.objects.get(ma_nhom=group_id)
#
#         # Kiểm tra người dùng có phải thành viên được duyệt của nhóm không
#         membership = ThanhVienNhom.objects.filter(
#             ma_nhom=nhom,
#             ma_nguoi_dung=nguoi_dung,
#             trang_thai='Được duyệt'
#         ).first()
#         if not membership:
#             return JsonResponse({'success': False, 'error': 'Bạn không có quyền đăng bài trong nhóm này!'})
#
#         # Quản trị viên thì bài viết tự động duyệt
#         trang_thai = True if membership.vai_tro == 'Quản trị viên' else False
#
#         response_data = {
#             'success': True,
#             'trang_thai': 'Đã duyệt' if trang_thai else 'Chờ duyệt'
#         }
#
#         if request.headers.get('Content-Type') == 'application/json':
#             data = json.loads(request.body)
#             content = data.get('content', '')
#             post_type = data.get('type', 'text')
#             options = data.get('options', [])
#
#             if not content and post_type != 'poll':
#                 return JsonResponse({'success': False, 'error': 'Nội dung bài viết không được để trống!'})
#
#             if post_type == 'poll' and (not content or len(options) < 2):
#                 return JsonResponse({'success': False, 'error': 'Thăm dò ý kiến cần câu hỏi và ít nhất 2 tùy chọn!'})
#
#             bai_viet = BaiViet.objects.create(
#                 MaNhom=nhom,
#                 MaNguoiDung=nguoi_dung,
#                 NoiDung=content,
#                 ThoiGianDang=timezone.now(),
#                 TrangThai=trang_thai,
#                 LoaiBaiViet=post_type
#             )
#
#             response_data.update({
#                 'post_id': bai_viet.MaBaiViet,
#                 'ho_ten': nguoi_dung.ho_ten,
#                 'thoi_gian_dang': bai_viet.ThoiGianDang.strftime('%d/%m/%Y %H:%M'),
#                 'type': post_type,
#                 'content': content
#             })
#
#             if post_type == 'poll' and options:
#                 # Giả sử có model PollOption để lưu tùy chọn
#                 # Cần tạo model PollOption trong models.py với cấu trúc:
#                 # class PollOption(models.Model):
#                 #     MaBaiViet = models.ForeignKey(BaiViet, on_delete=models.CASCADE)
#                 #     NoiDung = models.CharField(max_length=255)
#                 for option in options:
#                     # PollOption.objects.create(MaBaiViet=bai_viet, NoiDung=option)
#                     pass  # Bỏ qua vì chưa có model PollOption
#                 response_data['options'] = options
#
#         else:  # Xử lý file upload (video, image, file)
#             form_data = request.FILES
#             file = form_data.get('file')
#             description = request.POST.get('description', '')
#             post_type = request.POST.get('type', 'file')
#
#             if not file:
#                 return JsonResponse({'success': False, 'error': 'Vui lòng chọn file để đăng!'})
#
#             # Lưu file vào storage
#             file_name = default_storage.save(f'uploads/{file.name}', file)
#             file_url = default_storage.url(file_name)
#
#             bai_viet = BaiViet.objects.create(
#                 MaNhom=nhom,
#                 MaNguoiDung=nguoi_dung,
#                 NoiDung=description,
#                 ThoiGianDang=timezone.now(),
#                 TrangThai=trang_thai,
#                 LoaiBaiViet=post_type,
#                 FileDinhKem=file
#             )
#
#             response_data.update({
#                 'post_id': bai_viet.MaBaiViet,
#                 'ho_ten': nguoi_dung.ho_ten,
#                 'thoi_gian_dang': bai_viet.ThoiGianDang.strftime('%d/%m/%Y %H:%M'),
#                 'type': post_type,
#                 'content': description,
#                 'media_data': file_url,
#                 'file_name': file.name
#             })
#
#         return JsonResponse(response_data)
#     except Nhom.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Nhóm không tồn tại!'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)})



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

# def chi_tiet_nhom_dathamgia(request, group_id):
#     try:
#         user = User.objects.get(username='tranvanb')
#     except User.DoesNotExist:
#         return render(request, 'social/error.html', {'message': 'Người dùng tranvanb không tồn tại!'})
#
#     try:
#         nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
#     except NguoiDung.DoesNotExist:
#         return render(request, 'social/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})
#
#     nhom = get_object_or_404(Nhom, ma_nhom=group_id)
#
#     membership = ThanhVienNhom.objects.filter(ma_nhom=nhom, ma_nguoi_dung=nguoi_dung).first()
#     is_member = membership and membership.trang_thai == 'Được duyệt' if membership else False
#     is_pending = membership and membership.trang_thai == 'Chờ duyệt' if membership else False
#
#     posts_with_wordcount = []
#     if is_member:
#         posts = BaiViet.objects.filter(
#             MaNhom=nhom,
#             TrangThai=True
#         ).select_related('MaNguoiDung').order_by('-ThoiGianDang')
#
#         for post in posts:
#             cleaned_content = ' '.join(post.NoiDung.split())
#             word_count = len(cleaned_content.strip().split())
#             posts_with_wordcount.append({
#                 'post': post,
#                 'word_count': word_count
#             })
#
#     context = {
#         'nhom': nhom,
#         'nguoi_dung': nguoi_dung,
#         'posts_with_wordcount': posts_with_wordcount,
#         'is_member': is_member,
#         'is_pending': is_pending,
#     }
#     return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html', context)
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

# def thanh_vien_nhom(request, ma_nhom):
#     # Lấy người dùng tranvanb
#     try:
#         tai_khoan_tranvanb = User.objects.get(username='tranvanb')
#         nguoi_dung_tranvanb = NguoiDung.objects.get(ma_tai_khoan=tai_khoan_tranvanb.id)
#     except User.DoesNotExist:
#         messages.error(request, 'Người dùng tranvanb không tồn tại trong hệ thống!')
#         return redirect('nhom_lam_qtrivien')
#     except NguoiDung.DoesNotExist:
#         messages.error(request, 'Thông tin người dùng tranvanb không được tìm thấy trong cơ sở dữ liệu!')
#         return redirect('nhom_lam_qtrivien')
#
#     nhom = get_object_or_404(Nhom, ma_nhom=ma_nhom)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung_tranvanb,
#         ma_nhom=nhom,
#         vai_tro='Quản trị viên',
#         trang_thai='Được duyệt'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền xem thành viên nhóm!')
#         return redirect('chi_tiet_nhom_qtrivien', ma_nhom=ma_nhom)
#
#     danh_sach_thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nhom=nhom,
#         trang_thai='Được duyệt'
#     ).select_related('ma_nguoi_dung')
#
#     return render(request, 'social/Nhom/thanh_vien_nhom.html', {
#         'nhom': nhom,
#         'danh_sach_thanh_vien': danh_sach_thanh_vien,
#         'nguoi_dung': nguoi_dung_tranvanb
#     })
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
# View chi tiết nhóm làm quản trị viên
# def chi_tiet_nhom_qtrivien(request, group_id):
#     try:
#         user = User.objects.get(username='tranvanb')
#         nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
#     except (User.DoesNotExist, NguoiDung.DoesNotExist):
#         messages.error(request, 'Không tìm thấy thông tin người dùng!')
#         return redirect('group')
#
#     # Lấy thông tin nhóm
#     nhom = get_object_or_404(Nhom, ma_nhom=group_id)
#
#     # Kiểm tra xem người dùng có phải quản trị viên của nhóm không
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         vai_tro='Quản trị viên',
#         trang_thai='Được duyệt'
#     ).first()
#
#     if not thanh_vien:
#         messages.error(request, 'Bạn không có quyền xem chi tiết nhóm này!')
#         return redirect('nhom_lam_qtrivien')
#
#     # Lấy danh sách nhóm làm quản trị viên và nhóm đã tham gia để hiển thị trong sidebar
#     nhom_lam_qtrivien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         vai_tro='Quản trị viên',
#         trang_thai='Được duyệt'
#     ).select_related('ma_nhom')
#
#     admin_group_ids = nhom_lam_qtrivien.values_list('ma_nhom_id', flat=True)
#     nhom_da_tham_gia = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         trang_thai='Được duyệt'
#     ).exclude(ma_nhom_id__in=admin_group_ids).select_related('ma_nhom')
#
#     # Lấy danh sách bài viết của nhóm
#     posts = BaiViet.objects.filter(
#         MaNhom=nhom,
#         TrangThai=True
#     ).select_related('MaNguoiDung').order_by('-ThoiGianDang')
#
#     # Tạo danh sách bài viết với số lượt thích và trạng thái đã thích
#     posts_with_details = []
#     for post in posts:
#         word_count = len(post.NoiDung.strip().split())
#         # Kiểm tra xem người dùng đã thích bài viết này chưa
#         has_liked = CamXuc.objects.filter(
#             MaBaiViet=post,
#             MaNguoiDung=nguoi_dung,
#             LoaiCamXuc='Thích'
#         ).exists()
#         posts_with_details.append({
#             'post': post,
#             'word_count': word_count,
#             'like_count': post.SoLuongCamXuc,
#             'has_liked': has_liked
#         })
#
#     return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', {
#         'nhom': nhom,
#         'nhom_lam_qtrivien': nhom_lam_qtrivien,
#         'nhom_da_tham_gia': nhom_da_tham_gia,
#         'nguoi_dung': nguoi_dung,
#         'posts_with_details': posts_with_details
#     })
# @require_POST
# def submit_comment(request, post_id):
#     try:
#         user = request.user
#         nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
#     except (User.DoesNotExist, NguoiDung.DoesNotExist):
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=400)
#
#     post = get_object_or_404(BaiViet, MaBaiViet=post_id)
#     content = request.POST.get('content')
#
#     if not content:
#         return JsonResponse({'success': False, 'message': 'Nội dung bình luận không được để trống!'}, status=400)
#
#     BinhLuan.objects.create(
#         MaBaiViet=post,
#         MaNguoiDung=nguoi_dung,
#         NoiDung=content,
#         ThoiGianDang=timezone.now()
#     )
#
#     return JsonResponse({'success': True, 'message': 'Bình luận đã được gửi!'})
#
# @require_POST
# def send_invite(request, group_id):
#     try:
#         user = request.user
#         nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
#     except (User.DoesNotExist, NguoiDung.DoesNotExist):
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=400)
#
#     nhom = get_object_or_404(Nhom, ma_nhom=group_id)
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         vai_tro='Quản trị viên',
#         trang_thai='Được duyệt'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền mời thành viên!'}, status=403)
#
#     data = json.loads(request.body)
#     friend_ids = data.get('friend_ids', [])
#
#     for friend_id in friend_ids:
#         try:
#             friend = NguoiDung.objects.get(ma_nguoi_dung=friend_id)
#             ThanhVienNhom.objects.update_or_create(
#                 ma_nhom=nhom,
#                 ma_nguoi_dung=friend,
#                 defaults={'vai_tro': 'Thành viên', 'trang_thai': 'Chờ duyệt', 'thoi_gian_tham_gia': timezone.now()}
#             )
#         except NguoiDung.DoesNotExist:
#             continue
#
#     return JsonResponse({'success': True, 'message': 'Lời mời đã được gửi!'})

# View cho Bảng tin nhóm
#def chi_tiet_nhom_qtrivien(request, group_id):
    #group = Group.objects.get(id=group_id)
    #return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', {'group': group})
# View xử lý xoá nhóm
# @require_POST
# def delete_group(request, group_id):
#     try:
#         user = User.objects.get(username='tranvanb')
#         nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
#     except (User.DoesNotExist, NguoiDung.DoesNotExist):
#         return JsonResponse({'success': False, 'message': 'Không tìm thấy thông tin người dùng!'}, status=400)
#
#     nhom = get_object_or_404(Nhom, ma_nhom=group_id)
#
#     # Kiểm tra quyền quản trị viên
#     thanh_vien = ThanhVienNhom.objects.filter(
#         ma_nguoi_dung=nguoi_dung,
#         ma_nhom=nhom,
#         vai_tro='Quản trị viên',
#         trang_thai='Được duyệt'
#     ).first()
#
#     if not thanh_vien:
#         return JsonResponse({'success': False, 'message': 'Bạn không có quyền xoá nhóm này!'}, status=403)
#
#     # Cập nhật trạng thái nhóm thành 'Bị xóa'
#     nhom.trang_thai_nhom = 'Bị xóa'
#     nhom.save()
#
#     # Cập nhật trạng thái của tất cả thành viên thành 'Bị xóa'
#     ThanhVienNhom.objects.filter(ma_nhom=nhom).update(trang_thai='Bị xóa')
#
#     return JsonResponse({'success': True, 'message': 'Nhóm đã bị xoá thành công!'})
# # View cho Phê duyệt thành viên
# def duyet_thanh_vien(request):
#     return render(request, 'social/Nhom/duyet_thanh_vien.html')
#
# # View cho Phê duyệt bài viết
# def duyet_bai_viet(request):
#
#     return render(request, 'social/Nhom/duyet_bai_viet.html')
# def ket_qua_tim_kiem(request):
#     search_query = request.GET.get('search', '')  # Lấy giá trị tìm kiếm từ URL
#     return render(request, 'social/Nhom/group_search_results.html')
#
# # View cho Thành viên của nhóm
# def thanh_vien_nhom(request):
#     return render(request, 'social/Nhom/thanh_vien_nhom.html')



def profile(request):
    return render(request, 'social/profile.html')



def home(request):
    return render(request, 'social/home.html')  # Đảm bảo rằng bạn đang trả về tệp home.html

def search(request):
    return render(request,'social/search.html')

def message(request):
    return render(request, 'social/message.html')

# View chính cho nhóm
# View chính cho nhóm
def group(request):
    try:
        user = User.objects.get(username='tranvanb')
        nguoi_dung = NguoiDung.objects.get(ma_tai_khoan=user.id)
    except (User.DoesNotExist, NguoiDung.DoesNotExist):
        return render(request, 'social/error.html', {'message': 'Không tìm thấy thông tin người dùng!'})

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

def extracurricular(request):
    return render(request, 'social/extracurricular.html')

def extracurricular_detail(request):
    return render(request, 'social/extracurricular_detail.html')

def schedule(request):
    return render(request, 'social/dat_lich/schedule.html')
def calendar_view(request):
    return render(request, 'social/dat_lich/calendar.html')

def notif(request):
    return render(request, 'social/notif.html')

def more(request):
    return render(request, 'social/more.html')
def register(request):
    return render(request, 'register.html')

def admin_extracurr(request):
    return render(request, 'social/admin/admin_extracurr.html')

def admin_group(request):
    return render(request, 'social/admin/admin_group.html')


from django.shortcuts import render
def admin_schedule(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/admin/admin_Schedule/admin_schedule.html', {'stadiums': stadiums})

from django.shortcuts import render
from datetime import datetime, timedelta

import csv
from django.shortcuts import render
from datetime import datetime, timedelta
from .forms import UploadFileForm
from .models import Booking  # Giả sử bạn có model Booking

def calendar_view(request):
    # Tạo danh sách ngày
    start_date = datetime(2025, 3, 10)
    days = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        days.append({
            'name': ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật'][i],
            'date': day.day
        })

    times = ['17:00', '18:00', '19:00', '20:00']

    bookings = Booking.objects.all()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:

                date = datetime.strptime(row['date'], '%d/%m/%Y')
                time = datetime.strptime(row['time'], '%H:%M')
                is_canceled = row['is_canceled'].lower() == 'true'
                # Lưu vào database
                Booking.objects.create(
                    date=date,
                    time=time,
                    is_canceled=is_canceled
                )
        else:
            return render(request, 'social/dat_lich/calendar.html', {
                'form': form,
                'error': 'Có lỗi khi upload file.',
                'days': days,
                'times': times,
                'bookings': bookings
            })
    else:
        form = UploadFileForm()

    return render(request, 'social/dat_lich/calendar.html', {
        'form': form,
        'days': days,
        'times': times,
        'bookings': bookings
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Post  # Giả sử bạn có model Post


@require_POST
def create_post(request):
    try:
        data = json.loads(request.body)
        content = data.get('content')

        if not content:
            return JsonResponse({'success': False, 'error': 'Nội dung không được để trống'})

        # Tạo bài viết mới
        post = Post.objects.create(
            user=request.user,
            content=content
        )

        return JsonResponse({'success': True, 'post_id': post.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# View đăng nhập
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Kiểm tra xem email có tồn tại trong hệ thống không
            tai_khoan = TaiKhoan.objects.get(Email=email)

            # Kiểm tra mật khẩu
            if tai_khoan.MatKhau == password:  # Trong thực tế nên dùng hàm băm mật khẩu
                # Đăng nhập thành công
                request.session['user_id'] = tai_khoan.MaTaiKhoan
                return redirect('home')
            else:
                #kiểm tra mk
                messages.error(request, 'Email hoặc mật khẩu không chính xác')
        except TaiKhoan.DoesNotExist:
            #ktra tk
            messages.error(request, 'Email hoặc mật khẩu không chính xác')

    return render(request, 'social/login/login.html')


# View đăng xuất
def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')


# View đăng ký
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Kiểm tra mật khẩu xác nhận
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return render(request, 'social/login/register.html')

        # Kiểm tra email đã tồn tại chưa
        if TaiKhoan.objects.filter(Email=email).exists():
            messages.error(request, 'Email đã được sử dụng')
            return render(request, 'social/login/register.html')

        # Tạo tài khoản mới
        tai_khoan = TaiKhoan.objects.create(
            Email=email,
            MatKhau=password  # Trong thực tế nên mã hóa mật khẩu
        )

        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('login')

    return render(request, 'social/login/register.html')


# View quên mật khẩu
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Kiểm tra email có tồn tại không
        if not TaiKhoan.objects.filter(Email=email).exists():
            messages.error(request, 'Email không tồn tại trong hệ thống')
            return render(request, 'social/login/forgot_password.html')

        # Tạo mã OTP mới
        # Xóa các mã OTP cũ của email này
        OTP.objects.filter(email=email).delete()

        # Tạo mã OTP mới
        otp = OTP.objects.create(email=email)

        # Gửi email chứa mã OTP
        subject = 'Mã xác nhận đặt lại mật khẩu DUE Social'
        message = f'Mã xác nhận của bạn là: {otp.otp_code}. Mã này có hiệu lực trong 10 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            # Lưu email vào session để sử dụng ở các bước tiếp theo
            request.session['reset_email'] = email
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f'Không thể gửi email: {str(e)}')

    return render(request, 'social/login/forgot_password.html')


# View xác thực OTP
def verify_otp_view(request):
    if 'reset_email' not in request.session:
        return redirect('forgot_password')

    email = request.session['reset_email']

    if request.method == 'POST':
        # Lấy mã OTP từ form
        otp_digits = []
        for i in range(1, 5):
            digit = request.POST.get(f'otp{i}', '')
            otp_digits.append(digit)

        entered_otp = ''.join(otp_digits)

        # Kiểm tra mã OTP
        try:
            otp_obj = OTP.objects.filter(email=email, is_used=False).latest('created_at')

            if not otp_obj.is_valid():
                messages.error(request, 'Mã OTP đã hết hạn')
                return render(request, 'social/login/verify_otp.html')

            if otp_obj.otp_code != entered_otp:
                messages.error(request, 'Mã OTP không chính xác')
                return render(request, 'social/login/verify_otp.html')

            # OTP hợp lệ, đánh dấu đã sử dụng
            otp_obj.is_used = True
            otp_obj.save()

            # Chuyển đến trang đặt lại mật khẩu
            return redirect('reset_password')

        except OTP.DoesNotExist:
            messages.error(request, 'Mã OTP không tồn tại hoặc đã được sử dụng')

    return render(request, 'social/login/verify_otp.html')


# View đặt lại mật khẩu
def reset_password_view(request):
    if 'reset_email' not in request.session:
        return redirect('forgot_password')

    email = request.session['reset_email']

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Kiểm tra mật khẩu xác nhận
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return render(request, 'social/login/reset_password.html')

        # Cập nhật mật khẩu
        try:
            tai_khoan = TaiKhoan.objects.get(Email=email)
            tai_khoan.MatKhau = new_password  # Trong thực tế nên mã hóa mật khẩu
            tai_khoan.save()

            # Xóa session
            del request.session['reset_email']

            messages.success(request, 'Đặt lại mật khẩu thành công! Vui lòng đăng nhập.')
            return redirect('login')
        except TaiKhoan.DoesNotExist:
            messages.error(request, 'Không tìm thấy tài khoản')

    return render(request, 'social/login/reset_password.html')



from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import json
import random
import string
from django.utils import timezone
from datetime import timedelta
from .models import TaiKhoan, NguoiDung, OTP, PendingRegistration


# Giữ lại các view hiện có...

# View đăng ký
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Kiểm tra mật khẩu xác nhận
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return render(request, 'social/login/register.html')

        # Kiểm tra email đã tồn tại chưa
        if TaiKhoan.objects.filter(Email=email).exists():
            messages.error(request, 'Email đã được sử dụng')
            return render(request, 'social/login/register.html')

        # Xóa đăng ký chờ xác thực cũ nếu có
        PendingRegistration.objects.filter(email=email).delete()

        # Tạo đăng ký chờ xác thực mới
        pending_reg = PendingRegistration.objects.create(
            email=email,
            password=password  # Trong thực tế nên mã hóa mật khẩu
        )

        # Gửi email chứa mã OTP
        subject = 'Xác nhận đăng ký tài khoản DUE Social'
        message = f'Cảm ơn bạn đã đăng ký tài khoản DUE Social. Mã xác nhận của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            # Lưu email vào session để sử dụng ở bước xác thực OTP
            request.session['register_email'] = email
            return redirect('verify_register_otp')
        except Exception as e:
            messages.error(request, f'Không thể gửi email: {str(e)}')
            pending_reg.delete()  # Xóa đăng ký chờ xác thực nếu không gửi được email

    return render(request, 'social/login/register.html')


# View xác thực OTP đăng ký
def verify_register_otp_view(request):
    if 'register_email' not in request.session:
        return redirect('register')

    email = request.session['register_email']

    if request.method == 'POST':
        # Lấy mã OTP từ form
        otp_digits = []
        for i in range(1, 5):
            digit = request.POST.get(f'otp{i}', '')
            otp_digits.append(digit)

        entered_otp = ''.join(otp_digits)

        # Kiểm tra mã OTP
        try:
            pending_reg = PendingRegistration.objects.get(email=email, is_verified=False)

            if not pending_reg.is_valid():
                messages.error(request, 'Mã OTP đã hết hạn. Vui lòng đăng ký lại.')
                del request.session['register_email']
                pending_reg.delete()
                return redirect('register')

            if pending_reg.otp_code != entered_otp:
                messages.error(request, 'Mã OTP không chính xác. Vui lòng thử lại.')
                return render(request, 'social/login/verify_register_otp.html')

            # OTP hợp lệ, tạo tài khoản mới
            tai_khoan = TaiKhoan.objects.create(
                Email=email,
                MatKhau=pending_reg.password  # Trong thực tế nên mã hóa mật khẩu
            )

            # Đánh dấu đã xác thực và xóa session
            pending_reg.is_verified = True
            pending_reg.save()
            del request.session['register_email']

            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('login')

        except PendingRegistration.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')
            return redirect('register')

    return render(request, 'social/login/verify_register_otp.html')


# View gửi lại mã OTP đăng ký
def resend_register_otp_view(request):
    if 'register_email' not in request.session:
        return redirect('register')

    email = request.session['register_email']

    try:
        pending_reg = PendingRegistration.objects.get(email=email, is_verified=False)

        # Tạo mã OTP mới
        pending_reg.otp_code = ''.join(random.choices(string.digits, k=4))
        pending_reg.expires_at = timezone.now() + timedelta(minutes=30)
        pending_reg.save()

        # Gửi email chứa mã OTP mới
        subject = 'Mã xác nhận đăng ký tài khoản DUE Social'
        message = f'Mã xác nhận mới của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)
        messages.success(request, 'Đã gửi lại mã xác nhận. Vui lòng kiểm tra email của bạn.')

    except PendingRegistration.DoesNotExist:
        messages.error(request, 'Không tìm thấy thông tin đăng ký hoặc đã hết hạn.')

    return redirect('verify_register_otp')


def stadium_list(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/dat_lich/schedule.html', {'stadiums': stadiums})
def Xemdanhsach(request):

    confirmed_schedules = ConfirmedSchedule.objects.all()
    return render(request, 'social/admin/admin_Schedule/Xemdanhsach.html', {'confirmed_schedules': confirmed_schedules})
def schedule_view(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/dat_lich/schedule.html', {'stadiums': stadiums})

def Choduyet(request):
    pendings = PendingSchedule.objects.all()
    return render(request, 'social/admin/admin_Schedule/Choduyet.html', {'pendings': pendings})

from django.contrib import messages
from .models import PendingSchedule, ConfirmedSchedule

def Xacnhan(request, pending_id):

    pending = PendingSchedule.objects.get(id=pending_id)

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

    messages.success(request, "Lịch đăng ký đã được duyệt")

    return redirect('Choduyet')

def Huy(request, pending_id):
    pending = PendingSchedule.objects.get(id=pending_id)
    pending.status = 'cancelled'
    pending.save()
    return redirect('Choduyet')
from django.shortcuts import render, redirect, get_object_or_404
def HuyXemdanhsach(request, schedule_id):

    schedule = get_object_or_404(ConfirmedSchedule, id=schedule_id)

    schedule.status = "cancelled"
    schedule.save()

    messages.success(request, "Lịch đã được hủy thành công.")

    return redirect('Xemdanhsach')










##views nhóm admin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages


# Giả sử bạn có các model sau
# from .models import Group, GroupMembership, Post, MembershipRequest, PostApprovalRequest
# from .forms import GroupForm, PostForm

# Danh sách nhóm
@login_required
def nhom_list(request):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # groups = Group.objects.all()
    # user_groups = request.user.groups.all()
    # admin_groups = Group.objects.filter(admins=request.user)

    context = {
        # 'groups': groups,
        # 'user_groups': user_groups,
        # 'admin_groups': admin_groups,
    }
    return render(request, 'social/nhom_admin/nhom_list.html', context)


# Chi tiết nhóm (bảng tin)
@login_required
def nhom_detail(request, nhom_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)
    # posts = Post.objects.filter(group=group, is_approved=True).order_by('-created_at')

    # Kiểm tra quyền truy cập
    # if not group.is_member(request.user) and not group.is_admin(request.user):
    #     messages.error(request, "Bạn không có quyền truy cập nhóm này.")
    #     return redirect('nhom_list')

    context = {
        # 'group': group,
        # 'posts': posts,
        # 'is_admin': group.is_admin(request.user),
    }
    return render(request, 'social/nhom_admin/nhom_detail.html', context)


# Phê duyệt thành viên
@login_required
def nhom_approve_members(request, nhom_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     messages.error(request, "Bạn không có quyền quản trị nhóm này.")
    #     return redirect('nhom_detail', nhom_id=nhom_id)

    # member_requests = MembershipRequest.objects.filter(group=group, status='pending')

    context = {
        # 'group': group,
        # 'member_requests': member_requests,
    }
    return render(request, 'social/nhom_admin/nhom_approve_members.html', context)


# Phê duyệt bài viết
@login_required
def nhom_approve_posts(request, nhom_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     messages.error(request, "Bạn không có quyền quản trị nhóm này.")
    #     return redirect('nhom_detail', nhom_id=nhom_id)

    # pending_posts = PostApprovalRequest.objects.filter(group=group, status='pending')

    context = {
        # 'group': group,
        # 'pending_posts': pending_posts,
    }
    return render(request, 'social/nhom_admin/nhom_approve_posts.html', context)


# Quản lý thành viên
@login_required
def nhom_members(request, nhom_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     messages.error(request, "Bạn không có quyền quản trị nhóm này.")
    #     return redirect('nhom_detail', nhom_id=nhom_id)

    # members = GroupMembership.objects.filter(group=group, status='active')

    context = {
        # 'group': group,
        # 'members': members,
    }
    return render(request, 'social/nhom_admin/nhom_members.html', context)


# API xóa nhóm
@login_required
@require_POST
def api_delete_group(request, nhom_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa nhóm này.'})

    # Xóa nhóm
    # group.delete()

    return JsonResponse({'success': True, 'message': 'Nhóm đã được xóa thành công.'})


# API mời thành viên
@login_required
@require_POST
def api_invite_members(request, nhom_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền mời thành viên.'})

    # Lấy danh sách user_id từ request
    # user_ids = request.POST.getlist('user_ids')

    # Mời thành viên
    # for user_id in user_ids:
    #     user = get_object_or_404(User, id=user_id)
    #     invitation = GroupInvitation.objects.create(group=group, user=user, invited_by=request.user)
    #     # Gửi thông báo cho user

    return JsonResponse({'success': True, 'message': 'Đã gửi lời mời thành công.'})


# API phê duyệt thành viên
@login_required
@require_POST
def api_approve_member(request, nhom_id, user_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)
    # user = get_object_or_404(User, id=user_id)
    # member_request = get_object_or_404(MembershipRequest, group=group, user=user, status='pending')

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt thành viên.'})

    # Phê duyệt thành viên
    # member_request.status = 'approved'
    # member_request.save()
    # GroupMembership.objects.create(group=group, user=user, status='active')

    return JsonResponse({'success': True, 'message': 'Đã phê duyệt thành viên thành công.'})


# API từ chối thành viên
@login_required
@require_POST
def api_reject_member(request, nhom_id, user_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)
    # user = get_object_or_404(User, id=user_id)
    # member_request = get_object_or_404(MembershipRequest, group=group, user=user, status='pending')

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối thành viên.'})

    # Từ chối thành viên
    # member_request.status = 'rejected'
    # member_request.save()

    return JsonResponse({'success': True, 'message': 'Đã từ chối thành viên thành công.'})


# API xóa thành viên
@login_required
@require_POST
def api_remove_member(request, nhom_id, user_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)
    # user = get_object_or_404(User, id=user_id)
    # membership = get_object_or_404(GroupMembership, group=group, user=user, status='active')

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền xóa thành viên.'})

    # Xóa thành viên
    # membership.status = 'removed'
    # membership.save()

    return JsonResponse({'success': True, 'message': 'Đã xóa thành viên thành công.'})


# API phê duyệt bài viết
@login_required
@require_POST
def api_approve_post(request, nhom_id, post_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)
    # post = get_object_or_404(Post, id=post_id, group=group, is_approved=False)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền phê duyệt bài viết.'})

    # Phê duyệt bài viết
    # post.is_approved = True
    # post.save()

    return JsonResponse({'success': True, 'message': 'Đã phê duyệt bài viết thành công.'})


# API từ chối bài viết
@login_required
@require_POST
def api_reject_post(request, nhom_id, post_id):
    # Trong thực tế, bạn sẽ truy vấn dữ liệu từ database
    # group = get_object_or_404(Group, id=nhom_id)
    # post = get_object_or_404(Post, id=post_id, group=group, is_approved=False)

    # Kiểm tra quyền quản trị
    # if not group.is_admin(request.user):
    #     return JsonResponse({'success': False, 'message': 'Bạn không có quyền từ chối bài viết.'})

    # Từ chối bài viết
    # post.is_rejected = True
    # post.save()

    return JsonResponse({'success': True, 'message': 'Đã từ chối bài viết thành công.'})

