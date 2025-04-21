from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('message/', views.message, name='message'),
    path('group/', views.group, name='group'),
    path('extracurricular/', views.extracurricular, name='extracurricular'),
    path('extracurricular_detail/', views.extracurricular_detail, name='extracurricular_detail'),
    path('schedule/', views.stadium_list, name='schedule'),
    # Xóa dòng này để tránh xung đột
    # path('register/', views.notif, name='register'),
    path('notif/', views.notif, name='notification'),
    path('profile/', views.profile, name='profile'),

    path('nhom-da-tham-gia/', views.nhom_da_tham_gia, name='nhom_da_tham_gia'),
    path('chi-tiet-nhom-dathamgia/', views.chi_tiet_nhom_dathamgia, name='chi_tiet_nhom_dathamgia'),
    path('nhom-lam-qtrivien/', views.nhom_lam_qtrivien, name='nhom_lam_qtrivien'),
    path('chi-tiet-nhom-qtrivien/', views.chi_tiet_nhom_qtrivien, name='chi_tiet_nhom_qtrivien'),
    path('duyet-thanh-vien/', views.duyet_thanh_vien, name='duyet_thanh_vien'),
    path('duyet-bai-viet/', views.duyet_bai_viet, name='duyet_bai_viet'),
    path('thanh-vien-nhom/', views.thanh_vien_nhom, name='thanh_vien_nhom'),
    path('ket-qua-tim-kiem/', views.ket_qua_tim_kiem, name='ket_qua_tim_kiem_nhom'),

    path('GV/admin_extracurr/', views.admin_extracurr, name='admin_extracurr'),
    path('GV/admin_extracurr/check', views.admin_extracurr_check, name='admin_extracurr_check'),
    path('GV/admin_extracurr/detail', views.admin_extracurr_detail, name='admin_extracurr_detail'),

    path('GV/admin_group/', views.admin_group, name='admin_group'),
    path('GV/admin_schedule/', views.admin_schedule, name='admin_schedule'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('create-post/', views.create_post, name='create_post'),

    # URL pattern cho chức năng đăng nhập, đăng ký và quên mật khẩu
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

    # URL đăng ký với OTP
    path('verify-register-otp/', views.verify_register_otp_view, name='verify_register_otp'),
    path('resend-register-otp/', views.resend_register_otp_view, name='resend_register_otp'),
]

from django.conf.urls.static import static
from django.conf import settings
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)