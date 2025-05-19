from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('message/', views.message_view, name='message'),
    path('message/<int:hoi_thoai_id>/', views.message_view, name='message'),
    path('create-group/', views.create_group, name='create_group'),
    path('group/', views.group, name='group'),
    path('extracurricular/', views.extracurricular, name='extracurricular'),
    path('extracurricular/<int:pk>/', views.extracurricular_detail, name='extracurricular_detail'),
    path('schedule/', views.stadium_list, name='schedule'),
    path('vote-poll/<int:post_id>/<int:option_id>/', views.vote_poll, name='vote_poll'),
    # Xóa dòng này để tránh xung đột
    # path('register/', views.notif, name='register'),
    path('social/notif/', views.notif, name='notification'),
    path('profile/', views.profile, name='profile'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('get-comments/<int:post_id>/', views.get_comments, name='get_comments'),


    # path('nhom_admin-da-tham-gia/', views.nhom_da_tham_gia, name='nhom_da_tham_gia'),
    # path('chi-tiet-nhom_admin-dathamgia/', views.chi_tiet_nhom_dathamgia, name='chi_tiet_nhom_dathamgia'),
    # path('nhom_admin-lam-qtrivien/', views.nhom_lam_qtrivien, name='nhom_lam_qtrivien'),
    # path('chi-tiet-nhom_admin-qtrivien/', views.chi_tiet_nhom_qtrivien, name='chi_tiet_nhom_qtrivien'),
    # path('duyet-thanh-vien/', views.duyet_thanh_vien, name='duyet_thanh_vien'),
    # path('duyet-bai-viet/', views.duyet_bai_viet, name='duyet_bai_viet'),
    # path('thanh-vien-nhom_admin/', views.thanh_vien_nhom, name='thanh_vien_nhom'),
    # path('ket-qua-tim-kiem/', views.ket_qua_tim_kiem, name='ket_qua_tim_kiem_nhom'),
# path('ket-qua-tim-kiem-nhom/', views.ket_qua_tim_kiem_nhom, name='ket_qua_tim_kiem_nhom'),
    path('nhom-da-tham-gia/', views.nhom_da_tham_gia, name='nhom_da_tham_gia'),
    # path('dang-bai-viet/', views.post_article, name='post_article'),
    path('tham-gia-nhom/', views.join_group, name='join_group'),
    path('chi-tiet-nhom-dathamgia/<int:group_id>/', views.chi_tiet_nhom_dathamgia, name='chi_tiet_nhom_dathamgia'),
    path('ket-qua-tim-kiem-nhom/', views.search_groups, name='ket_qua_tim_kiem_nhom'),
path('chi-tiet-nhom-quan-tri-vien/<int:MaNhom>/', views.chi_tiet_nhom_quan_tri_vien, name='chi_tiet_nhom_qtrivien'),
path('post-article/', views.post_article, name='post_article'),
    path('binh-luan/<int:ma_bai_viet>/', views.them_binh_luan, name='them_binh_luan'),
    path('like-post/<int:ma_bai_viet>/', views.like_post, name='like_post'),
    path('group/', views.group_feed, name='group_feed'),
    path('', views.group_list, name='group_list'),
    path('tao-nhom-moi/', views.tao_nhom_moi, name='tao_nhom_moi'),
    path('nhom-lam-quantrivien/', views.nhom_lam_qtrivien, name='nhom_lam_qtrivien'),  # Sửa view tại đây
    # path('chi-tiet-nhom-qtrivien/<int:group_id>/', views.chi_tiet_nhom_qtrivien, name='chi_tiet_nhom_qtrivien'),
    # path('chi-tiet-nhom-quan-tri-vien/<int:ma_nhom>/', views.chi_tiet_nhom_quan_tri_vien, name='chi_tiet_nhom_qtrivien'),
    path('gui-binh-luan/<int:ma_bai_viet>/', views.gui_binh_luan, name='submit_comment'),
    path('gui-moi/<int:ma_nhom>/', views.gui_moi, name='send_invite'),
    path('duyet-thanh-vien/<int:MaNhom>/', views.duyet_thanh_vien, name='duyet_thanh_vien'),
    path('duyet-bai-viet/<int:MaNhom>/', views.duyet_bai_viet, name='duyet_bai_viet'),
    path('thanh-vien-nhom/<int:MaNhom>/', views.thanh_vien_nhom, name='thanh_vien_nhom'),
    path('duyet-thanh-vien-xac-nhan/<int:ma_nhom>/<int:ma_thanh_vien>/', views.duyet_thanh_vien_xac_nhan,
         name='approve_member'),
    path('tu-choi-thanh-vien/<int:ma_nhom>/<int:ma_thanh_vien>/', views.tu_choi_thanh_vien, name='reject_member'),
    path('duyet-bai-viet-xac-nhan/<int:ma_nhom>/<int:ma_bai_viet>/', views.duyet_bai_viet_xac_nhan,
         name='approve_post'),
    path('tu-choi-bai-viet/<int:ma_nhom>/<int:ma_bai_viet>/', views.tu_choi_bai_viet, name='reject_post'),
    path('xoa-thanh-vien/<int:ma_nhom>/<int:ma_thanh_vien>/', views.xoa_thanh_vien, name='remove_member'),
    path('search-users/', views.search_users, name='search_users'),
path('test-template/', views.test_template, name='test_template'),
path('vote-poll/<int:post_id>/<int:option_id>/', views.vote_poll, name='vote_poll'),

    # URL cho đổi mật khẩu (Thêm mới)
    path('change-password/', views.change_password, name='change_password'),



    path('GV/admin_extracurr/', views.admin_extracurr, name='admin_extracurr'),
    path('GV/admin_extracurr/<int:pk>/', views.admin_extracurr_detail, name='admin_extracurr_detail'),
    path('GV/admin_group/', views.admin_group, name='admin_group'),
    path('GV/admin_schedule/', views.admin_schedule, name='admin_schedule'),

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
    path('cho-duyet/', views.Choduyet, name='Choduyet'),
path('huy-xemdanhsach/<int:schedule_id>/', views.HuyXemdanhsach, name='HuyXemdanhsach'),
path('calendar/', views.calendar_view, name='calendar_view'),
path('xemdanhsach/', views.Xemdanhsach, name='Xemdanhsach'),  # Đảm bảo view Xemdanhsach đã được định nghĩa
    path('xacnhan/<int:pending_id>/', views.Xacnhan, name='Xacnhan'),  # Đảm bảo view Xacnhan đã được định nghĩa
    path('huy/<int:pending_id>/', views.Huy, name='Huy'),



    #nhom_admin
    path('nhom_admin/', views.nhom_list, name='nhom_list'),
    path('nhom_admin/<int:nhom_id>/', views.nhom_detail, name='nhom_detail'),
    path('nhom_admin/<int:nhom_id>/phe-duyet-thanh-vien/', views.nhom_approve_members, name='nhom_approve_members'),
    path('nhom_admin/<int:nhom_id>/phe-duyet-bai-viet/', views.nhom_approve_posts, name='nhom_approve_posts'),
    path('nhom_admin/<int:nhom_id>/thanh-vien/', views.nhom_members, name='nhom_members'),

    # API cho các chức năng AJAX
    path('api/nhom_admin/<int:nhom_id>/xoa/', views.api_delete_group, name='api_delete_group'),
    path('api/nhom_admin/<int:nhom_id>/moi-thanh-vien/', views.api_invite_members, name='api_invite_members'),
    path('api/nhom_admin/<int:nhom_id>/phe-duyet-thanh-vien/<int:user_id>/', views.api_approve_member,
         name='api_approve_member'),
    path('api/nhom_admin/<int:nhom_id>/tu-choi-thanh-vien/<int:user_id>/', views.api_reject_member, name='api_reject_member'),
    path('api/nhom_admin/<int:nhom_id>/xoa-thanh-vien/<int:user_id>/', views.api_remove_member, name='api_remove_member'),
    path('api/nhom_admin/<int:nhom_id>/phe-duyet-bai-viet/<int:post_id>/', views.api_approve_post, name='api_approve_post'),
    path('api/nhom_admin/<int:nhom_id>/tu-choi-bai-viet/<int:post_id>/', views.api_reject_post, name='api_reject_post'),

    path('search_users/', views.search_users, name='search_users'),
    path('start_conversation/', views.start_conversation, name='start_conversation'),


]

from django.conf.urls.static import static
from django.conf import settings
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
