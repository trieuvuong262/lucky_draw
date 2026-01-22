import openpyxl  # <--- Đã thêm thư viện này
from django.contrib import admin
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Participant, Prize

class ParticipantResource(resources.ModelResource):
    class Meta:
        model = Participant
        # Thêm 'is_on_duty' vào danh sách trường cho phép import/export
        fields = ('name', 'department', 'is_on_duty')
        import_id_fields = ('name', 'department')
        exclude = ('id', 'is_winner', 'won_prize', 'checkin_time')

@admin.register(Participant)
class ParticipantAdmin(ImportExportModelAdmin):
    resource_class = ParticipantResource
    
    # Hiển thị cột 'is_on_duty' (icon dấu check/gạch chéo)
    list_display = ('name', 'department', 'is_on_duty', 'is_winner', 'won_prize', 'checkin_time')
    
    # Thêm bộ lọc 'is_on_duty' để Admin dễ dàng tìm người đang trực
    list_filter = ('is_on_duty', 'is_winner', 'department', 'won_prize')
    
    search_fields = ('name', 'department')
    list_per_page = 50
    
    # Cho phép sửa nhanh trạng thái trực ngay ở danh sách mà không cần bấm vào chi tiết
    list_editable = ('is_on_duty',) 
    
    actions = ['download_sample_file', 'reset_winner_status']

    @admin.action(description='⬇️ Tải file mẫu (Name, Dept, Is On Duty)')
    def download_sample_file(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Import Template"
        
        # Cập nhật Header thêm cột is_on_duty
        headers = ['name', 'department', 'is_on_duty']
        ws.append(headers)
        
        # Dữ liệu mẫu: 1 là Có trực (True), 0 là Không trực (False)
        sample_data = [
            ['Nguyễn Văn An', 'Kế Toán', 1],
            ['Trần Thị Bưởi', 'Nhân Sự', 0],
            ['Lê Văn Cam', 'IT (Phần mềm)', 0],
            ['Phạm Văn Dũng', 'Bảo Vệ', 1],
        ]
        
        for row in sample_data:
            ws.append(row)
            
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=mau_import_nhan_vien_v2.xlsx'
        wb.save(response)
        return response

    @admin.action(description='Reset trạng thái (Hủy trúng giải)')
    def reset_winner_status(self, request, queryset):
        rows_updated = queryset.update(is_winner=False, won_prize=None)
        self.message_user(request, f"Đã reset trạng thái cho {rows_updated} người tham gia!")

@admin.register(Prize)
class PrizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'get_remaining', 'order')
    list_editable = ('quantity', 'order') # Cho phép sửa nhanh số lượng ngay ở list
    ordering = ('order',)
    
    def get_remaining(self, obj):
        return obj.remaining_count()
    get_remaining.short_description = 'Còn lại'

# Tùy chỉnh tiêu đề trang Admin
admin.site.site_header = "Hệ thống Lucky Draw YEP"
admin.site.site_title = "Quản trị Lucky Draw"
admin.site.index_title = "Danh sách quản lý"