from django.shortcuts import render
from .models import Stadium


def nhom_da_tham_gia(request):
    # Lấy dữ liệu hoặc bất kỳ logic nào bạn cần cho trang này
    return render(request, 'social/Nhom/nhom_da_tham_gia.html')
def chi_tiet_nhom_dathamgia(request):
    # Lấy dữ liệu hoặc bất kỳ logic nào bạn cần cho trang này
    return render(request, 'social/Nhom/chi_tiet_nhom_dathamgia.html')
def nhom_lam_qtrivien(request):
    # Lấy dữ liệu hoặc bất kỳ logic nào bạn cần cho trang này
    return render(request, 'social/Nhom/nhom_lam_qtrivien.html')
def chi_tiet_nhom_qtrivien(request):
    # Lấy dữ liệu hoặc bất kỳ logic nào bạn cần cho trang này
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

def admin_schedule(request):
    return render(request, 'social/admin/admin_schedule.html')

from django.shortcuts import render


def stadium_list(request):
    stadiums = Stadium.objects.all()
    return render(request, 'social/dat_lich/schedule.html', {'stadiums': stadiums})


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

    # Tạo danh sách khung giờ
    times = ['17:00', '18:00', '19:00', '20:00']

    # Lấy dữ liệu bookings từ database
    bookings = Booking.objects.all()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            # Giả sử file là CSV
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                # Giả sử file CSV có các cột: date, time, is_canceled
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