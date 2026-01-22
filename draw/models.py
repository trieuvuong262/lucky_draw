from django.db import models
class Prize(models.Model):
    name = models.CharField(max_length=100) # VD: Giải Đặc Biệt
    quantity = models.IntegerField(default=1) # Số lượng giải
    order = models.IntegerField(default=0) 
    def __str__(self):
        return f"{self.name} (Còn lại: {self.remaining_count()})"
    def remaining_count(self):
        return self.quantity - self.participant_set.count()
class Participant(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    is_on_duty = models.BooleanField(default=False, verbose_name="Đang trực")
    is_winner = models.BooleanField(default=False)
    checkin_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    won_prize = models.ForeignKey(Prize, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name