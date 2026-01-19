# app/models.py
from django.db import models

class Prize(models.Model):
    name = models.CharField(max_length=100) # VD: Giải Đặc Biệt
    quantity = models.IntegerField(default=1) # Số lượng giải
    # Trường này để sắp xếp hiển thị trên dropdown (1: KK, 2: Ba, 3: Nhì...)
    order = models.IntegerField(default=0) 
    
    def __str__(self):
        return f"{self.name} (Còn lại: {self.remaining_count()})"

    def remaining_count(self):
        # Đếm số giải còn lại
        return self.quantity - self.participant_set.count()

class Participant(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    is_winner = models.BooleanField(default=False)
    checkin_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # Liên kết người thắng với giải nào
    won_prize = models.ForeignKey(Prize, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name