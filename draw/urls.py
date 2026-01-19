from django.urls import path
from . import views
urlpatterns = [
    path('', views.checkin_page, name='checkin'), 
    path('api/checkin/', views.api_checkin, name='api_checkin'),
    path('screen/', views.big_screen, name='big_screen'),
    path('api/get_participants/', views.api_get_participants, name='get_users'),
    path('api/draw_winner/', views.api_draw_winner, name='draw'),
    path('api/unlock_checkin/', views.api_unlock_checkin, name='api_unlock_checkin'),
]