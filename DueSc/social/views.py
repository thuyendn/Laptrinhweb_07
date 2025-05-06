from django.shortcuts import render
from .models import Stadium, PendingSchedule

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
    return render(request, 'social/home.html')  # Đảm bảo rằng bạn đang trả về tệp home.html

def search(request):
    return render(request,'social/search.html')

def message(request):
    return render(request, 'social/message.html')

def group(request):
    return render(request, 'social/group.html')



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

