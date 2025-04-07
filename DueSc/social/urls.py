from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('message/', views.message, name='message'),
    path('group/', views.group, name='group'),
    path('extracurricular/', views.extracurricular, name='extracurricular'),
    path('extracurricular_detail/', views.extracurricular_detail, name='extracurricular_detail'),
    path('schedule/', views.schedule, name='schedule'),
    path('notif/', views.notif, name='notification'),


    path('nhom-da-tham-gia/', views.nhom_da_tham_gia, name='nhom_da_tham_gia'),
    path('chi-tiet-nhom-dathamgia/', views.chi_tiet_nhom_dathamgia, name='chi_tiet_nhom_dathamgia'),
    path('nhom-lam-qtrivien/', views.nhom_lam_qtrivien, name='nhom_lam_qtrivien'),
    path('chi-tiet-nhom-qtrivien/', views.chi_tiet_nhom_qtrivien, name='chi_tiet_nhom_qtrivien'),
    path('duyet-thanh-vien/', views.duyet_thanh_vien, name='duyet_thanh_vien'),
    path('duyet-bai-viet/', views.duyet_bai_viet, name='duyet_bai_viet'),
    path('thanh-vien-nhom/', views.thanh_vien_nhom, name='thanh_vien_nhom'),
    path('ket-qua-tim-kiem/', views.ket_qua_tim_kiem, name='ket_qua_tim_kiem_nhom'),

    path('GV/admin_extracurr/', views.admin_extracurr, name='admin_extracurr'),
    path('GV/admin_group/', views.admin_group, name='admin_group'),
    path('GV/admin_schedule/', views.admin_schedule, name='admin_schedule'),

]
