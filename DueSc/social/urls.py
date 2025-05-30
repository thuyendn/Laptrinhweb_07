from django.urls import path
from . import views
from .views import notif, get_notification_count, mark_all_notifications_read, get_recent_notifications, \
    mark_notification_read

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('get-voters/<int:option_id>/', views.get_voters, name='get_voters'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('vote-poll/<int:post_id>/<int:option_id>/', views.vote_poll, name='vote_poll'),
    path('search/', views.search, name='search'),

    path('message/', views.message_view, name='message'),
    path('message/<int:hoi_thoai_id>/', views.message_view, name='message'),
    path('message/<int:hoi_thoai_id>/add-member/', views.add_member, name='add_member'),

    path('group/', views.group, name='group'),
    #thông báo
    path('social/notif/', views.notif, name='notification'),
    #profile
    path('profile/', views.profile, name='profile'),
    #like bài
    path('like-post/<int:ma_bai_viet>/', views.like_post, name='like_post'),
    #Linh
    path('like-post/<int:ma_bai_viet>/', views.like_post, name='like_post'),
    path('get-comments/<int:post_id>/', views.get_comments, name='get_comments'),
    path('nhom-da-tham-gia/', views.nhom_da_tham_gia, name='nhom_da_tham_gia'),
    path('post-article/<int:ma_nhom>/', views.post_article, name='post_article'),
    path('join-group/', views.join_group, name='join_group'),
    path('chi-tiet-nhom-dathamgia/<int:ma_nhom>/', views.chi_tiet_nhom_dathamgia, name='chi_tiet_nhom_dathamgia'),
    path('ket-qua-tim-kiem/', views.search_groups, name='search_groups'),
    path('tao-nhom-moi/', views.tao_nhom_moi, name='tao_nhom_moi'),
    path('nhom-lam-quantrivien/', views.nhom_lam_qtrivien, name='nhom_lam_qtrivien'),
    path('chi-tiet-nhom-quan-tri-vien/<int:ma_nhom>/', views.chi_tiet_nhom_quan_tri_vien, name='chi_tiet_nhom_qtrivien'),
    path('invite-to-group/<int:ma_nhom>/', views.gui_moi, name='gui_moi'),
    path('delete-group/<int:ma_nhom>/', views.delete_group, name='delete_group'),
    path('duyet-bai-viet/<int:ma_nhom>/view/', views.duyet_bai_viet, name='duyet_bai_viet'),
    path('thanh-vien-nhom/<int:ma_nhom>/', views.thanh_vien_nhom, name='thanh_vien_nhom'),
    path('duyet-bai-viet/<int:ma_nhom>/', views.duyet_bai_viet_action, name='duyet_bai_viet_action'),
    path('xoa-thanh-vien/<int:ma_nhom>/<int:member_id>/', views.xoa_thanh_vien, name='xoa_thanh_vien'),
    path('download/<path:file_path>/', views.download_file, name='download_file'),
    path('group-feed/', views.group_feed, name='group_feed'),
    path('duyet-thanh-vien/<int:ma_nhom>/', views.duyet_thanh_vien, name='duyet_thanh_vien'),
    path('duyet-thanh-vien-xac-nhan/<int:ma_nhom>/<int:ma_thanh_vien>/', views.duyet_thanh_vien_xac_nhan, name='duyet_thanh_vien_xac_nhan'),
    path('tu-choi-thanh-vien/<int:ma_nhom>/<int:ma_thanh_vien>/', views.tu_choi_thanh_vien, name='tu_choi_thanh_vien'),
    path('update-group-avatar/<int:ma_nhom>/', views.update_group_avatar, name='update_group_avatar'),
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    #Đổi MK
    path('change-password/', views.change_password, name='change_password'),
    path('GV/Extracurricular_admin/', views.admin_extracurr, name='Extracurricular_admin'),
    path('GV/Extracurricular_admin/search/', views.admin_search_activities, name='search_admin'),
    path('GV/Extracurricular_admin/<int:pk>/', views.admin_extracurr_detail, name='admin_extracurr_detail'),
    path('extracurricular/', views.extracurricular, name='extracurricular'),
    path('extracurricular/search/', views.search_activities, name='search_activities'),
    path('extracurricular/<int:pk>/', views.extracurricular_detail, name='extracurricular_detail'),
    path('nhom_admin/', views.nhom_list, name='admin_group'),  # Đổi để hiển thị nhom_list.html trước
    path('create-post/', views.create_post, name='create_post'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('verify-register-otp/', views.verify_register_otp_view, name='verify_register_otp'),
    #San
    path('danh_sach_san/', views.danh_sach_san, name='danh_sach_san'),
    path('choduyet/', views.choduyet, name='choduyet'),
    path('xemdanhsach/', views.xemdanhsach_view, name='xemdanhsach'),
    path('huy-xemdanhsach/<int:schedule_id>/', views.HuyXemdanhsach, name='HuyXemdanhsach'),
    path('lich_dat_san/', views.lich_dat_san_view, name='lich_dat_san_view'),
    path('xacnhan/<int:pending_id>/', views.Xacnhan, name='Xacnhan'),
    path('huy/<int:pending_id>/', views.Huy, name='Huy'),
    path('GV/danh_sach_san_admin/', views.danh_sach_san_admin, name='danh_sach_san_admin'),
    path('search_users/', views.search_users, name='search_users'),
    path('start_conversation/', views.start_conversation, name='start_conversation'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('resend-register-otp/', views.resend_register_otp_view, name='resend_register_otp'),
    # URL chính cho admin nhóm
    path('GV/nhom_admin/', views.nhom_admin_main, name='admin_group'),
    path('GV/nhom_admin/<int:nhom_id>/', views.admin_group_detail, name='admin_group_detail'),
    path('GV/nhom_admin/<int:nhom_id>/phe-duyet-thanh-vien/', views.nhom_approve_members, name='admin_group_approve_members'),
    path('GV/nhom_admin/<int:nhom_id>/phe-duyet-bai-viet/', views.nhom_approve_posts, name='admin_group_approve_posts'),
    path('GV/nhom_admin/<int:nhom_id>/thanh-vien/', views.nhom_members, name='admin_group_members'),

    path('GV/nhom_admin/api/groups/<int:nhom_id>/approve/', views.api_approve_group_admin, name='admin_api_approve_group'),
    path('GV/nhom_admin/api/groups/<int:nhom_id>/reject/', views.api_reject_group_admin, name='admin_api_reject_group'),
    path('GV/nhom_admin/api/member-requests/<int:request_id>/approve/', views.api_approve_member_request, name='admin_api_approve_member_request'),
    path('GV/nhom_admin/api/member-requests/<int:request_id>/reject/', views.api_reject_member_request, name='admin_api_reject_member_request'),
    path('GV/nhom_admin/api/posts/<int:post_id>/approve/', views.api_approve_post_request, name='admin_api_approve_post_request'),
    path('GV/nhom_admin/api/posts/<int:post_id>/reject/', views.api_reject_post_request, name='admin_api_reject_post_request'),
    path('GV/nhom_admin/api/members/<int:member_id>/remove/', views.api_remove_member_from_group, name='admin_api_remove_member'),
    path('GV/nhom_admin/search/', views.search_groups_admin, name='admin_search_groups'),
    path('search_users/', views.search_usersmess, name='search_users'),
    path('api/search-users/', views.search_usersmess, name='search_users_api'),
    path('api/start-conversation/', views.start_conversation, name='start_conversation'),
    path('GV/nhom_admin/list/',views.nhom_admin_list,name='nhom_admin_list'),
    path('GV/nhom_admin/create/',	 views.create_group_admin,	 name='create_group_admin'),
    path('GV/nhom_admin/api/delete_group/<int:nhom_id>/',views.api_delete_group,name='api_delete_group'),
    path('create-group/', views.create_groupmess, name='create_groupmess'),
    path('message/', views.message_view, name='message'),
    path('message/<int:hoi_thoai_id>/', views.message_view, name='message'),
    #xóa chat
    path('api/get-unread-messages-count/', views.get_unread_messages_count, name='get_unread_messages_count'),
    path('api/delete-conversation/<int:hoi_thoai_id>/', views.delete_conversation, name='delete_conversation'),
    #Them tv
path('message/<int:hoi_thoai_id>/add-member/', views.add_member, name='add_member'),
    #xem thông tin user từ tìm kiếm
    path('get-user-details/<int:user_id>/', views.get_user_details, name='get_user_details'),
    # Thông báo
    path('notif/', notif, name='notif'),
    path('get-notification-count/', get_notification_count, name='get_notification_count'),
    path('mark-notification-read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
    path('mark-all-notifications-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    path('get-recent-notifications/', get_recent_notifications, name='get_recent_notifications'),
]
from django.conf.urls.static import static
from django.conf import settings
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)