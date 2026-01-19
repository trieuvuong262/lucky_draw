import openpyxl
from django.contrib import admin
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Participant, Prize

# --- 1. CẤU HÌNH IMPORT EXCEL (LOGIC XỬ LÝ FILE) ---
class ParticipantResource(resources.ModelResource):
    class Meta:
        model = Participant
        # Chỉ nhận diện và xử lý 2 cột này
        fields = ('name', 'department')
        
        # Dùng 'name' và 'department' làm khóa duy nhất để nhận diện
        # (Không cần cột ID trong file Excel)
        import_id_fields = ('name', 'department')
        
        # Loại bỏ các cột không cần thiết khi import để tránh lỗi
        exclude = ('id', 'is_winner', 'won_prize', 'checkin_time')

# --- 2. QUẢN LÝ NGƯỜI THAM GIA ---
@admin.register(Participant)
class ParticipantAdmin(ImportExportModelAdmin):
    resource_class = ParticipantResource
    
    # Hiển thị trên bảng danh sách
    list_display = ('name', 'department', 'is_winner', 'won_prize', 'checkin_time')
    list_filter = ('is_winner', 'department', 'won_prize')
    search_fields = ('name', 'department')
    list_per_page = 50

    # Các hành động (Actions)
    actions = ['download_sample_file', 'reset_winner_status']

    # --- Action 1: Tải file mẫu Excel ---
    @admin.action(description='⬇️ Tải file mẫu (Chỉ Name & Dept)')
    def download_sample_file(self, request, queryset):
        # Tạo workbook mới
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Import Template"

        # Tạo Header (Phải khớp chính xác với fields trong Resource)
        headers = ['name', 'department']
        ws.append(headers)

        # Tạo vài dòng dữ liệu mẫu cho user dễ hiểu
        sample_data = [
            ['Nguyễn Văn An', 'Kế Toán'],
            ['Trần Thị Bưởi', 'Nhân Sự'],
            ['Lê Văn Cam', 'IT (Phần mềm)'],
        ]
        for row in sample_data:
            ws.append(row)

        # Trả về response dạng file download
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=mau_import_nhan_vien.xlsx'
        wb.save(response)
        return response

    # --- Action 2: Reset trạng thái trúng giải ---
    @admin.action(description='Reset trạng thái (Hủy trúng giải)')
    def reset_winner_status(self, request, queryset):
        rows_updated = queryset.update(is_winner=False, won_prize=None)
        self.message_user(request, f"Đã reset trạng thái cho {rows_updated} người tham gia!")

# --- 3. QUẢN LÝ GIẢI THƯỞNG ---
@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'get_remaining', 'order')
    list_editable = ('quantity', 'order') # Cho phép sửa nhanh số lượng ngay ở list
    ordering = ('order',)
    
    def get_remaining(self, obj):
        return obj.remaining_count()
    get_remaining.short_description = 'Còn lại'

# --- 4. TÙY CHỈNH TÊN HEADER ADMIN ---
admin.site.site_header = "Hệ thống Lucky Draw YEP"
admin.site.site_title = "Quản trị Lucky Draw"
admin.site.index_title = "Danh sách quản lý"