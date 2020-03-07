from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'how_to_play/', views.instr, name='how_to_play'),
    path(r'select_difficulty/', views.select_difficulty, name='select_difficulty'),
    path(r'create_question/', views.create_question, name='create_question'),
    path(r'update_db/', views.update_score_to_db, name='update_db'),
    path(r'get_highest_score/', views.get_highest_score, name='get_highest_score'),
]
