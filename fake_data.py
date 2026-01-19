import os
import django
import random

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lucky_draw.settings') # Thay 'lucky_draw' bằng tên folder dự án của bạn nếu khác
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
    # Xóa hết dữ liệu cũ để test cho sạch (tùy chọn)
    Participant.objects.all().delete()
    
    print(f"Đang tạo {n} người dùng mẫu...")
    
    users = []
    for i in range(n):
        # Random tên
        ho = random.choice(ho_list)
        dem = random.choice(dem_list)
        ten = random.choice(ten_list)
        full_name = f"{ho} {dem} {ten}"
        
        # Random bộ phận
        dept = random.choice(departments)
        
        # Tạo đối tượng (nhưng chưa lưu vào DB ngay để dùng bulk_create cho nhanh)
        users.append(Participant(name=full_name, department=dept))

    # Lưu 1 lần vào DB (Tốc độ cực nhanh)
    Participant.objects.bulk_create(users)
    print(f"✅ Đã tạo thành công {n} nhân viên!")

if __name__ == "__main__":
    generate_data(200) # Bạn muốn tạo 300 người cho đầy màn hình thì sửa số này