from django.shortcuts import render


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
    return render(request, 'social/schedule.html')

def notif(request):
    return render(request, 'social/notif.html')

def more(request):
    return render(request, 'social/more.html')


def admin_extracurr(request):
    return render(request, 'social/admin/admin_extracurr.html')

def admin_group(request):
    return render(request, 'social/admin/admin_group.html')

def admin_schedule(request):
    return render(request, 'social/admin/admin_schedule.html')