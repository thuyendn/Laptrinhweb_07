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
    return render(request, 'social/admin/admin_schedule.html', {'stadiums': stadiums})

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
    return render(request, 'social/admin/Xemdanhsach.html', {'confirmed_schedules': confirmed_schedules})
def schedule_view(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/dat_lich/schedule.html', {'stadiums': stadiums})

def Choduyet(request):
    pendings = PendingSchedule.objects.all()
    return render(request, 'social/admin/Choduyet.html', {'pendings': pendings})

from django.contrib import messages
from .models import PendingSchedule, ConfirmedSchedule

def Xacnhan(request, pending_id):

    pending = PendingSchedule.objects.get(id=pending_id)

    ConfirmedSchedule.objects.create(
        student_id=pending.student_id,
        name=pending.name,
        phone=pending.phone,
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