from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('message/', views.message, name='message'),
    path('group/', views.group, name='group'),
    path('extracurricular/', views.extracurricular, name='extracurricular'),
    path('schedule/', views.stadium_list, name='schedule'),

    path('register/', views.notif, name='register'),
    path('notif/', views.notif, name='notification'),
    path('more/', views.more, name='more'),

    path('GV/admin_extracurr/', views.admin_extracurr, name='admin_extracurr'),
    path('GV/admin_group/', views.admin_group, name='admin_group'),
    path('GV/admin_schedule/', views.admin_schedule, name='admin_schedule'),
]
from django.conf.urls.static import static
from django.conf import settings
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar'),
]