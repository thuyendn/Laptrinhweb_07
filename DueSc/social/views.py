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
from django.contrib.auth.models import User
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

