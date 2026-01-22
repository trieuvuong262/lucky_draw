from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Participant, Prize
import random
IS_CHECKIN_LOCKED = False
def checkin_page(request):
    return render(request, 'checkin.html')
def big_screen(request):
    if not Prize.objects.exists():
        Prize.objects.create(name="Giải Khuyến Khích", quantity=10, order=1)
        Prize.objects.create(name="Giải Ba", quantity=3, order=2)
        Prize.objects.create(name="Giải Nhì", quantity=2, order=3)
        Prize.objects.create(name="Giải Nhất", quantity=1, order=4)
        Prize.objects.create(name="Giải Đặc Biệt", quantity=1, order=5)
    prizes = Prize.objects.all().order_by('order')
    return render(request, 'big_screen.html', {'prizes': prizes})
def api_get_participants(request):
    participants = Participant.objects.all().values('id', 'name', 'department', 'is_winner')
    return JsonResponse({'users': list(participants)})
@csrf_exempt
def api_checkin(request):
    global IS_CHECKIN_LOCKED 
    if request.method == 'POST':
        if IS_CHECKIN_LOCKED:
            return JsonResponse({
                'status': 'error', 
                'message': 'Cổng Check-in đã ĐÓNG! Đã bắt đầu quay số.'
            })
        if request.session.get('has_checked_in', False):
             return JsonResponse({'status': 'error', 'message': 'Máy này đã đăng ký rồi!'})
        raw_name = request.POST.get('name', '')
        dept = request.POST.get('department', '')
        if not raw_name:
            return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập Họ Tên'})
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
    # global IS_CHECKIN_LOCKED 
    if request.method == 'POST':
        # IS_CHECKIN_LOCKED = True 
        prize_id = request.POST.get('prize_id')
        try:
            prize = Prize.objects.get(id=prize_id)
        except Prize.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Giải thưởng không tồn tại'})
        if prize.quantity <= 0:
            return JsonResponse({'status': 'error', 'message': 'Giải này đã hết!'})
        candidates = Participant.objects.filter(is_winner=False)
        if not candidates.exists():
            return JsonResponse({'status': 'error', 'message': 'Không còn ai để quay!'})
        winner = random.choice(list(candidates))
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
                'prize_name': prize.name,
                'is_on_duty': winner.is_on_duty
            }
        })
    return JsonResponse({'status': 'error'})
def api_unlock_checkin(request):
    global IS_CHECKIN_LOCKED
    IS_CHECKIN_LOCKED = False
    return JsonResponse({'status': 'success', 'message': 'Đã mở lại cổng Check-in!'})

@csrf_exempt
def api_toggle_checkin(request):
    global IS_CHECKIN_LOCKED
    if request.method == 'POST':
        action = request.POST.get('action') # Nhận lệnh 'lock' hoặc 'unlock'
        
        if action == 'lock':
            IS_CHECKIN_LOCKED = True
            message = "Đã ĐÓNG cổng Check-in. Không ai có thể vào được nữa."
        elif action == 'unlock':
            IS_CHECKIN_LOCKED = False
            message = "Đã MỞ cổng Check-in. Mọi người có thể tiếp tục đăng ký."
        else:
            return JsonResponse({'status': 'error', 'message': 'Lệnh không hợp lệ'})
            
        return JsonResponse({
            'status': 'success', 
            'message': message, 
            'is_locked': IS_CHECKIN_LOCKED
        })