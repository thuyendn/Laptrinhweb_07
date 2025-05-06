from django.contrib.auth import authenticate, login
from django.shortcuts import render
from .models import Stadium, PendingSchedule, Like, Comment, PollOption
from django.contrib.auth.decorators import login_required


def nhom_da_tham_gia(request):
    return render(request, 'social/Nhom/nhom_da_tham_gia.html')
def chi_tiet_nhom_dathamgia(request):
    return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html')
def nhom_lam_qtrivien(request):
    return render(request, 'social/Nhom/nhom_lam_qtrivien.html')
def chi_tiet_nhom_qtrivien(request):
    return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html')
# View cho Bảng tin nhóm
#def chi_tiet_nhom_qtrivien(request, group_id):
    #group = Group.objects.get(id=group_id)
    #return render(request, 'social/Nhom/chi_tiet_nhom_qtrivien.html', {'group': group})

# View cho Phê duyệt thành viên
def duyet_thanh_vien(request):
    return render(request, 'social/Nhom/duyet_thanh_vien.html')

# View cho Phê duyệt bài viết
def duyet_bai_viet(request):

    return render(request, 'social/Nhom/duyet_bai_viet.html')
def ket_qua_tim_kiem(request):
    search_query = request.GET.get('search', '')  # Lấy giá trị tìm kiếm từ URL
    return render(request, 'social/Nhom/group_search_results.html')

# View cho Thành viên của nhóm
def thanh_vien_nhom(request):
    return render(request, 'social/Nhom/thanh_vien_nhom.html')



def profile(request):
    return render(request, 'social/profile.html')


def home(request):
    posts = Post.objects.all().order_by('-created_at')
    liked_posts = []
    if request.user.is_authenticated:
        liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    context = {
        'posts': posts,
        'liked_posts': liked_posts,
    }
    return render(request, 'social/home.html', context)



def search(request):
    return render(request,'social/search.html')

def message(request):
    return render(request, 'social/message.html')

def group(request):
    return render(request, 'social/group.html')



def schedule(request):
    return render(request, 'social/dat_lich/schedule.html')



def notif(request):
    return render(request, 'social/notif.html')

def more(request):
    return render(request, 'social/more.html')
def register(request):
    return render(request, 'register.html')

#SINH VIEN NGOAI KHOA
def phan_loai_nk_SV(nguoi_dung):
    now = timezone.now()

    # Lấy ID của các hoạt động "sẽ tham gia"
    se_tham_gia_ids = DKNgoaiKhoa.objects.filter(
        ma_sv=nguoi_dung,
        trang_thai=DKNgoaiKhoa.TrangThai.KHONG_THAM_GIA,
        ma_hd_nk__thoi_gian__gt=now
    ).values_list('ma_hd_nk_id', flat=True)

    # Lấy ID của các hoạt động "đã tham gia"
    da_tham_gia_ids = DKNgoaiKhoa.objects.filter(
        ma_sv=nguoi_dung,
        trang_thai=DKNgoaiKhoa.TrangThai.DA_THAM_GIA,
        ma_hd_nk__thoi_gian__lte=now
    ).values_list('ma_hd_nk_id', flat=True)

    # Truy vấn lại để lấy thông tin chi tiết hoạt động
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
    # Lấy thông tin hoạt động ngoại khoá
    activity = get_object_or_404(HoatDongNgoaiKhoa, pk=pk)
    se_tham_gia, da_tham_gia = phan_loai_nk_SV(nguoi_dung)

    # Truyền thông tin vào context
    return render(request,
                  'social/extracurricular_detail.html',
                  {'activity': activity,
                   'se_tham_gia': se_tham_gia,
                   'da_tham_gia': da_tham_gia,
                   })


# ADMIN NGOẠI KHOÁ
from .forms import ExtracurricularForm
from .models import DKNgoaiKhoa, NguoiDung, HoatDongNgoaiKhoa


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
        # Lấy đối tượng DKNgoaiKhoa từ ID sinh viên và hoạt động
        dknk = DKNgoaiKhoa.objects.get(id=sinh_vien_id, ma_hd_nk=activity)

        # Cập nhật trạng thái tham gia
        dknk.trang_thai = DKNgoaiKhoa.TrangThai.DA_THAM_GIA
        dknk.save()

        # Thông báo thành công
        messages.success(request, f"Đã xác nhận tham gia cho sinh viên {dknk.ma_sv.ho_ten}")
    except DKNgoaiKhoa.DoesNotExist:
        # Thông báo nếu không tìm thấy sinh viên
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
    # Giả lập người dùng có ma_nguoi_dung = 2
    request.user.nguoidung = NguoiDung.objects.get(ma_nguoi_dung=2)

    if request.method == 'POST':
        success, form = process_extracurricular_form(request, ExtracurricularForm, request.user.nguoidung)
        if success:
            return redirect('admin_extracurr')
    else:
        form = ExtracurricularForm()

    chua_dien_ra, da_dien_ra = phan_loai_nk_GV()
    activities = HoatDongNgoaiKhoa.objects.order_by('-ma_nk')

    return render(request, 'social/admin/admin_extracurr/admin_extracurr.html',
                  { 'form': form,
                    'activities': activities,
                    'chua_dien_ra': chua_dien_ra,
                    'da_dien_ra': da_dien_ra })


def admin_extracurr_detail(request, pk):
    # Lấy thông tin hoạt động ngoại khoá
    activity = get_object_or_404(HoatDongNgoaiKhoa, pk=pk)
    request.user.nguoidung = NguoiDung.objects.get(ma_nguoi_dung=2)

    # Lấy danh sách các sinh viên đã đăng ký tham gia hoạt động này
    sinh_vien_dang_ky = DKNgoaiKhoa.objects.filter(ma_hd_nk=activity)

    sinh_vien_list = []
    for dk in sinh_vien_dang_ky:
        sinh_vien = {
            'ho_ten': dk.ma_sv.ho_ten,
            'ma_tai_khoan': dk.ma_sv.ma_tai_khoan,
            'ma_nguoi_dung': dk.ma_sv.ma_nguoi_dung,
            'trang_thai': dk.trang_thai,
            'ngoaikhoa_id':dk.id
        }
        sinh_vien_list.append(sinh_vien)

    # Tổng số đăng ký
    so_luong_dk = sinh_vien_dang_ky.count()

    # Số lượng đã tham gia
    so_luong_da_tham_gia = sinh_vien_dang_ky.filter(trang_thai='DA_THAM_GIA').count()

    # Xử lý form nếu có
    if request.method == 'POST':
        # Kiểm tra nếu có nút duyệt từng sinh viên
        if 'duyet_sinh_vien' in request.POST:
            sinh_vien_id = request.POST.get('sinh_vien_id')
            duyet_tung_sinh_vien(request, activity, sinh_vien_id)  # Gọi hàm đã tách ra
            return redirect('admin_extracurr_detail', pk=pk)

        if 'duyet_all' in request.POST:  # Duyệt tất cả sinh viên
            so_duyet = duyet_tat_ca_SV(request, activity)
            messages.success(request, f"Đã duyệt {so_duyet} sinh viên.")
            return redirect('admin_extracurr_detail', pk=pk)
        else:
            success, form = process_extracurricular_form(request, ExtracurricularForm, request.user.nguoidung)
            if success:
                return redirect('admin_extracurr')
    else:
        # Khởi tạo form nếu là GET request
        form = ExtracurricularForm()


    # Phân loại hoạt động
    chua_dien_ra, da_dien_ra = phan_loai_nk_GV()
    trang_thai_hoat_dong = 'chua_dien_ra' if activity in chua_dien_ra else (
        'da_dien_ra' if activity in da_dien_ra else 'khac'
    )

    # Truyền thông tin vào context
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



from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def pending_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    pending_schedules = PendingSchedule.objects.filter(status='pending')
    context = {
        'pending_schedules': pending_schedules,
    }
    return render(request, 'social/admin/admin_Schedule/choduyet.html', context)

# (Giữ lại các view khác như Choduyet, Xacnhan, Huy nếu đã có)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import PendingSchedule, Stadium
from django.http import HttpResponseRedirect

def calendar_view(request):
    if request.method == 'POST':
        selected_date = request.POST.get('date')
        selected_time = request.POST.get('time')
        location = request.POST.get('location')
        name = request.user.username if request.user.is_authenticated else request.POST.get('name', 'Unknown')
        email = request.user.email if request.user.is_authenticated else request.POST.get('email', 'unknown@example.com')
        student_id = request.POST.get('student_id', '')

        if selected_date and selected_time and location:
            try:
                # Chuẩn hóa location
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
    return render(request, 'social/dat_lich/calendar.html', context)

@login_required
def Choduyet(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

<<<<<<< HEAD
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
=======
    location = request.GET.get('location', None)

    if not location:
        messages.error(request, 'Không tìm thấy địa điểm.')
        return redirect('admin_schedule')

    standardized_location = location
    print(f"Location from URL: {standardized_location}")  # Debug

    pendings = PendingSchedule.objects.filter(location=standardized_location, status='pending')
    print(f"Found {pendings.count()} items for location: {standardized_location}")  # Debug

    context = {
        'pendings': pendings,
        'location': standardized_location,
    }
    return render(request, 'social/admin/admin_Schedule/Choduyet.html', context)

@login_required
def Xacnhan(request, pending_id):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    try:
        pending = PendingSchedule.objects.get(id=pending_id, status='pending')
        pending.status = 'approved'
        pending.save()
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

def admin_schedule(request):
    # Lấy tất cả các sân
    stadiums = Stadium.objects.all()
    context = {
        'stadiums': stadiums,
    }
    return render(request, 'social/admin/admin_Schedule/admin_schedule.html', context)

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

@csrf_exempt
def book_slot(request):
    if request.method == "POST":
        data = json.loads(request.body) if request.body else {}
        date = data.get("date")
        time = data.get("time")

        # Kiểm tra xem khung giờ đã được đặt chưa
        for booking in bookings:
            if booking["date"] == date and booking["time"] == time and not booking["is_canceled"]:
                return JsonResponse({"success": False, "message": "Khung giờ này đã được đặt!"})

        # Thêm lịch đặt mới
        bookings.append({"date": date, "time": time, "is_canceled": False})
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "message": "Phương thức không hợp lệ!"})
>>>>>>> origin/chucnang_ngan
from django.views.decorators.http import require_POST
import json
from .models import Post  # Giả sử bạn có model Post





@login_required
@require_POST
def create_post(request):
    try:
        print("Received create_post request")
        print("User:", request.user)
        print("Authenticated:", request.user.is_authenticated)
        print("Is anonymous:", isinstance(request.user, AnonymousUser))
        print("POST data:", request.POST)
        print("FILES:", request.FILES)

        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser):
            print("User not authenticated or is anonymous")
            return JsonResponse({'success': False, 'error': 'Bạn cần đăng nhập để đăng bài viết'})

        content = request.POST.get('content')
        post_type = request.POST.get('post_type', 'text')
        print("Content:", content)
        print("Post Type:", post_type)

        if not content and post_type == 'text':
            print("Content is empty for text post")
            return JsonResponse({'success': False, 'error': 'Nội dung không được để trống'})

        post = Post.objects.create(
            user=request.user,
            content=content,
            post_type=post_type
        )
        print("Post created:", post.id)

        if post_type == 'image' and 'image' in request.FILES:
            print("Saving image file")
            post.image = request.FILES['image']
        elif post_type == 'video' and 'video' in request.FILES:
            print("Saving video file")
            post.video = request.FILES['video']
        elif post_type == 'file' and 'file' in request.FILES:
            print("Saving file")
            post.file = request.FILES['file']
        elif post_type == 'poll':
            print("Creating poll options")
            options = [request.POST.get(f'option_{i}') for i in range(1, 11) if request.POST.get(f'option_{i}')]
            print("Poll options:", options)
            if len(options) < 2:
                post.delete()
                return JsonResponse({'success': False, 'error': 'Thăm dò ý kiến cần ít nhất 2 lựa chọn'})
            for option_text in options:
                PollOption.objects.create(post=post, text=option_text)

        post.save()
        print("Post saved successfully")
        return JsonResponse({'success': True, 'post_id': post.id})
    except Exception as e:
        print("Error in create_post:", str(e))
        return JsonResponse({'success': False, 'error': str(e)})


from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# View đăng nhập
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = TaiKhoan.objects.filter(Email=email).first()
        if user and check_password(password, user.MatKhau):
            print(f"User {email} authenticated successfully")
            auth_login(request, user, backend='social.authentication.TaiKhoanBackend')
            print(f"User {email} logged in, session user: {request.user}")
            print(f"User authenticated: {request.user.is_authenticated}")
            return redirect('home')
        else:
            print(f"Authentication failed for {email}")
            messages.error(request, 'Email hoặc mật khẩu không đúng.')
            return render(request, 'social/login/login.html')

    return render(request, 'social/login/login.html')

# View đăng xuất
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')


# View đăng ký
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        ho_ten = request.POST.get('ho_ten')

        if not all([email, password, confirm_password]):
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
            password=password,  # Sẽ được mã hóa trong save()
            ho_ten = ho_ten
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

# View quên mật khẩu
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

# View xác thực OTP
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


# View đặt lại mật khẩu
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
# from django.contrib import messages
# from .models import TaiKhoan, NguoiDung, PendingRegistration
# def register_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')
#
#         if not all([email, password, confirm_password]):
#             messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
#             return render(request, 'social/login/register.html')
#
#         if password != confirm_password:
#             messages.error(request, 'Mật khẩu xác nhận không khớp.')
#             return render(request, 'social/login/register.html')
#
#         if TaiKhoan.objects.filter(Email=email).exists():
#             messages.error(request, 'Email đã được sử dụng.')
#             return render(request, 'social/login/register.html')
#
#         PendingRegistration.objects.filter(email=email).delete()
#
#         pending_reg = PendingRegistration.objects.create(
#             email=email,
#             password=password  # Sẽ được mã hóa trong save()
#         )
#
#         subject = 'Xác nhận đăng ký tài khoản DUE Social'
#         message = f'Mã xác nhận của bạn là: {pending_reg.otp_code}. Mã này có hiệu lực trong 30 phút.'
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = [email]
#
#         try:
#             send_mail(subject, message, from_email, recipient_list, fail_silently=False)
#             request.session['register_email'] = email
#             messages.success(request, 'Mã OTP đã được gửi đến email của bạn.')
#             return redirect('verify_register_otp')
#         except Exception as e:
#             messages.error(request, f'Không thể gửi email: {str(e)}')
#             pending_reg.delete()
#             return render(request, 'social/login/register.html')
#
#     return render(request, 'social/login/register.html')
#


# View xác thực OTP đăng ký
from django.contrib.auth.hashers import make_password, check_password


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

            nguoi_dung = NguoiDung.objects.create(
                ma_tai_khoan=None,
                ho_ten=pending_reg.ho_ten
            )
            tai_khoan = TaiKhoan.objects.create(
                Email=pending_reg.email,
                MatKhau=pending_reg.password,
                MaNguoiDung=nguoi_dung
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


# View gửi lại mã OTP đăng ký
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


def HuyXemdanhsach(request, schedule_id):

    schedule = get_object_or_404(ConfirmedSchedule, id=schedule_id)

    schedule.status = "cancelled"
    schedule.save()

    messages.success(request, "Lịch đã được hủy thành công.")

    return redirect('Xemdanhsach')

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
# views.py

##views nhóm admin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from django.contrib.auth.hashers import check_password
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

