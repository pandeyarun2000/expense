from django.urls import path
from .views import categorize_expense, upload_dataset
from . import views


urlpatterns = [
    path('', categorize_expense, name='categorize_expense'),
    path('upload-dataset/', upload_dataset, name='upload_dataset'),
    path('all_expenses/', views.all_expenses, name='all_expenses'),
    path('download_csv/', views.download_csv, name='download_csv'),
    
]
