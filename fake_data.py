import os
import django
import random

# Thiết lập môi trường Django
# Thay 'lucky_draw' bằng tên folder dự án chứa settings.py của bạn
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lucky_draw.settings') 
django.setup()

from draw.models import Participant

# Dữ liệu mẫu Tiếng Việt
ho_list = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
dem_list = ["Văn", "Thị", "Minh", "Ngọc", "Xuân", "Thu", "Đức", "Hữu", "Tuấn", "Hoàng", "Mai", "Lan", "Thanh", "Quang", "Gia", "Khánh"]
ten_list = ["Anh", "Tuấn", "Dũng", "Hoa", "Huệ", "Lan", "Mai", "Cường", "Bình", "Chi", "Ngọc", "Hùng", "Thắng", "Nam", "Bắc", "Trung", "Kiên", "Trang", "Hương", "Thảo", "Hà", "Linh"]
departments = [
    "Anesthesiology", "Biomedical", "Customer Service", "Diagnostic Imaging Department",
    "Emergency", "Facility Management", "Finance & Accounting", "General Internal Medicine",
    "General Planing", "General Surgery", "Hospital/Clinic/BUs BOM", "Human Resource",
    "Infection Control", "IT", "Laboratory", "Nephrology", "Nursing Management",
    "Obstetrics & Gynecology", "Operation", "Outpatient", "Pediatrics", "Pharmacy",
    "Procurement", "Quality Management", "Rehabilitation & Physical Therapy",
    "Sale & Marketing", "Support Service"
]

def generate_data(n=250):
    print("Đang xóa dữ liệu cũ...")
    # Xóa hết dữ liệu cũ để test cho sạch
    Participant.objects.all().delete()
    
    print(f"Đang tạo {n} người dùng mẫu...")
    
    users = []
    count_truc = 0 # Đếm xem có bao nhiêu người trực
    
    for i in range(n):
        # Random tên
        ho = random.choice(ho_list)
        dem = random.choice(dem_list)
        ten = random.choice(ten_list)
        full_name = f"{ho} {dem} {ten}"
        
        # Random bộ phận
        dept = random.choice(departments)
        
        # --- LOGIC MỚI: Random trạng thái TRỰC ---
        # random.random() trả về số từ 0.0 đến 1.0
        # < 0.15 nghĩa là khoảng 15% cơ hội sẽ là True (Đang trực)
        dang_truc = random.random() < 0.15 
        
        if dang_truc:
            count_truc += 1

        # Tạo đối tượng
        users.append(Participant(
            name=full_name, 
            department=dept,
            is_on_duty=dang_truc  # <-- Gán giá trị vào đây
        ))

    # Lưu 1 lần vào DB
    Participant.objects.bulk_create(users)
    print(f"✅ Đã tạo thành công {n} nhân viên!")
    print(f"   - Trong đó có {count_truc} người ĐANG TRỰC ({round(count_truc/n*100, 1)}%)")

if __name__ == "__main__":
    generate_data(200) # Tạo 200 người