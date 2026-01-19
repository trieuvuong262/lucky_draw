import openpyxl
from django.contrib import admin
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Participant, Prize
class ParticipantResource(resources.ModelResource):
    class Meta:
        model = Participant
        fields = ('name', 'department')
        import_id_fields = ('name', 'department')
        exclude = ('id', 'is_winner', 'won_prize', 'checkin_time')
@admin.register(Participant)
class ParticipantAdmin(ImportExportModelAdmin):
    resource_class = ParticipantResource
    list_display = ('name', 'department', 'is_winner', 'won_prize', 'checkin_time')
    list_filter = ('is_winner', 'department', 'won_prize')
    search_fields = ('name', 'department')
    list_per_page = 50
    actions = ['download_sample_file', 'reset_winner_status']
    @admin.action(description='⬇️ Tải file mẫu (Chỉ Name & Dept)')
    def download_sample_file(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Import Template"
        headers = ['name', 'department']
        ws.append(headers)
        sample_data = [
            ['Nguyễn Văn An', 'Kế Toán'],
            ['Trần Thị Bưởi', 'Nhân Sự'],
            ['Lê Văn Cam', 'IT (Phần mềm)'],
        ]
        for row in sample_data:
            ws.append(row)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=mau_import_nhan_vien.xlsx'
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
admin.site.site_header = "Hệ thống Lucky Draw YEP"
admin.site.site_title = "Quản trị Lucky Draw"
admin.site.index_title = "Danh sách quản lý"