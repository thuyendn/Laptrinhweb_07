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

def Choduyet(request):
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

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PendingSchedule
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PendingSchedule
from django.http import HttpResponseRedirect

# @login_required
# def Xacnhan(request, pending_id):
#     if not request.user.is_staff:
#         messages.error(request, 'Bạn không có quyền truy cập!')
#         return redirect('calendar_view')
#
#     try:
#         pending = PendingSchedule.objects.get(id=pending_id, status='pending')
#         pending.status = 'approved'
#         pending.save()
#         messages.success(request, 'Lịch đã được xác nhận thành công.')
#         return redirect('processed_list')  # Chuyển hướng đến danh sách đã xử lý
#     except PendingSchedule.DoesNotExist:
#         messages.error(request, 'Lịch không tồn tại hoặc đã được xử lý.')
#         return redirect('processed_list')
#
# @login_required
# def Huy(request, pending_id):
#     if not request.user.is_staff:
#         messages.error(request, 'Bạn không có quyền truy cập!')
#         return redirect('calendar_view')
#
#     try:
#         pending = PendingSchedule.objects.get(id=pending_id, status='pending')
#         pending.status = 'canceled'
#         pending.save()
#         messages.success(request, 'Lịch đã được hủy thành công.')
#         return redirect('processed_list')  # Chuyển hướng đến danh sách đã xử lý
#     except PendingSchedule.DoesNotExist:
#         messages.error(request, 'Lịch không tồn tại hoặc đã được xử lý.')
#         return redirect('processed_list')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PendingSchedule
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PendingSchedule
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PendingSchedule
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PendingSchedule
from django.http import HttpResponseRedirect


def Xacnhan(request, pending_id):
    try:
        # Debug: Kiểm tra tất cả các bản ghi với pending_id
        print(f"Attempting to get pending with id={pending_id}")
        pending = PendingSchedule.objects.get(id=pending_id)
        print(f"Found pending: {pending}, status={pending.status}")

        # Kiểm tra nếu trạng thái là 'pending'
        if pending.status != 'pending':
            messages.error(request, f'Lịch đã được xử lý trước đó (trạng thái: {pending.status}).')
            return redirect(f'/cho-duyet/?location={pending.location}')

        # Cập nhật trạng thái
        pending.status = 'approved'
        pending.save()
        messages.success(request, f'Lịch đã được xác nhận thành công.')
        return redirect(f'/cho-duyet/?location={pending.location}')
    except PendingSchedule.DoesNotExist:
        messages.error(request, f'Lịch không tồn tại.')
        return redirect(f'/cho-duyet/?location={request.GET.get("location", "")}')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PendingSchedule
from django.http import HttpResponseRedirect

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PendingSchedule
from django.http import HttpResponseRedirect


def Huy(request, pending_id):
    try:
        print(f"Attempting to get pending with id={pending_id}")
        pending = PendingSchedule.objects.get(id=pending_id)
        print(f"Found pending: {pending}, status={pending.status}")

        if pending.status != 'pending':
            print(f"Status is already {pending.status}, cannot cancel.")
            messages.error(request, f'Lịch đã được xử lý trước đó (trạng thái: {pending.status}).')
        else:
            print(f"Setting status to 'canceled' for pending {pending_id}")
            pending.status = 'canceled'  # Đảm bảo trạng thái là 'canceled'
            pending.save()
            print(f"After save, status={pending.status}")
            messages.success(request, f'Lịch đã được hủy thành công.')

        return redirect(f'/cho-duyet/?location={pending.location}')
    except PendingSchedule.DoesNotExist:
        messages.error(request, f'Lịch không tồn tại.')
        return redirect(f'/cho-duyet/?location={request.GET.get("location", "")}')
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
# @login_required
def processed_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập!')
        return redirect('calendar_view')

    approved_schedules = PendingSchedule.objects.filter(status='approved')
    canceled_schedules = PendingSchedule.objects.filter(status='canceled')
    context = {
        'approved_schedules': approved_schedules,
        'canceled_schedules': canceled_schedules,
    }
    return render(request, 'social/admin/admin_Schedule/Xemdanhsach.html', context)
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

