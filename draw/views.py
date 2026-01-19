from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Participant, Prize
import random
IS_CHECKIN_LOCKED = False
# 1. Trang Check-in cho Mobile
def checkin_page(request):
    return render(request, 'checkin.html')


def big_screen(request):
    # TỰ ĐỘNG TẠO GIẢI NẾU CHƯA CÓ (Setup 1 lần duy nhất)
    if not Prize.objects.exists():
        Prize.objects.create(name="Giải Khuyến Khích", quantity=10, order=1)
        Prize.objects.create(name="Giải Ba", quantity=3, order=2)
        Prize.objects.create(name="Giải Nhì", quantity=2, order=3)
        Prize.objects.create(name="Giải Nhất", quantity=1, order=4)
        Prize.objects.create(name="Giải Đặc Biệt", quantity=1, order=5)
    
    # Lấy danh sách giải để hiển thị lên menu
    prizes = Prize.objects.all().order_by('order')
    return render(request, 'big_screen.html', {'prizes': prizes})

# API lấy danh sách user để vẽ ô vuông (Frontend gọi mỗi 2s)
def api_get_participants(request):
    # Thêm 'department' vào danh sách lấy về
    participants = Participant.objects.all().values('id', 'name', 'department', 'is_winner')
    return JsonResponse({'users': list(participants)})
# 3. Logic Quay Số (Admin bấm nút gọi API này)
@csrf_exempt
def api_checkin(request):
    global IS_CHECKIN_LOCKED # Gọi biến toàn cục vào
    
    if request.method == 'POST':
        # --- 2. KIỂM TRA ĐÃ KHÓA HAY CHƯA ---
        if IS_CHECKIN_LOCKED:
            return JsonResponse({
                'status': 'error', 
                'message': 'Cổng Check-in đã ĐÓNG! Đã bắt đầu quay số.'
            })

        # ... (Đoạn code kiểm tra session cũ giữ nguyên) ...
        if request.session.get('has_checked_in', False):
             return JsonResponse({'status': 'error', 'message': 'Máy này đã đăng ký rồi!'})

        raw_name = request.POST.get('name', '')
        dept = request.POST.get('department', '')
        
        if not raw_name:
            return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập Họ Tên'})
        
        # Xử lý tên & Lưu DB (Giữ nguyên code cũ)
        formatted_name = raw_name.strip().title()
        typo_mapping = { "Quan": "Quang", "Tuan": "Tuấn", "Teo": "Tèo" }
        name_parts = formatted_name.split()
        fixed_parts = [typo_mapping.get(part, part) for part in name_parts]
        final_name = " ".join(fixed_parts)
        
        if Participant.objects.filter(name=final_name, department=dept).exists():
             return JsonResponse({'status': 'error', 'message': 'Bạn đã check-in rồi!'})

        Participant.objects.create(name=final_name, department=dept)
        request.session['has_checked_in'] = True
        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'status': 'error'})

@csrf_exempt
def api_draw_winner(request):
    global IS_CHECKIN_LOCKED # Gọi biến toàn cục vào

    if request.method == 'POST':
        # --- 3. BẬT CHẾ ĐỘ KHÓA NGAY KHI BẤM QUAY ---
        IS_CHECKIN_LOCKED = True 
        
        prize_id = request.POST.get('prize_id')
        try:
            prize = Prize.objects.get(id=prize_id)
        except Prize.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Giải thưởng không tồn tại'})

        if prize.quantity <= 0:
            return JsonResponse({'status': 'error', 'message': 'Giải này đã hết!'})

        # Lấy danh sách người chưa trúng
        candidates = Participant.objects.filter(is_winner=False)
        
        if not candidates.exists():
            return JsonResponse({'status': 'error', 'message': 'Không còn ai để quay!'})

        # Chọn người thắng ngẫu nhiên
        winner = random.choice(list(candidates))
        
        # Cập nhật DB
        winner.is_winner = True
        winner.won_prize = prize
        winner.save()
        
        prize.quantity -= 1
        prize.save()
        
        return JsonResponse({
            'status': 'success',
            'remaining': prize.quantity,
            'winner': {
                'id': winner.id,
                'name': winner.name,
                'department': winner.department,
                'prize_name': prize.name
            }
        })
    return JsonResponse({'status': 'error'})

# --- 4. THÊM API ĐỂ MỞ KHÓA (RESET) NẾU CẦN ---
# Bạn có thể gọi link này trên trình duyệt nếu muốn mở lại checkin: /api/unlock_checkin/
def api_unlock_checkin(request):
    global IS_CHECKIN_LOCKED
    IS_CHECKIN_LOCKED = False
    return JsonResponse({'status': 'success', 'message': 'Đã mở lại cổng Check-in!'})