from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('create/', views.CreateProfileView.as_view(), name='create_profile'),
    path('edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<int:user_id>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('discover/', views.DiscoverView.as_view(), name='discover'),
    path('photos/upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('photos/delete/<int:photo_id>/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('block/<int:user_id>/', views.BlockUserView.as_view(), name='block_user'),
    path('unblock/<int:user_id>/', views.UnblockUserView.as_view(), name='unblock_user'),
    path('report/<int:user_id>/', views.ReportUserView.as_view(), name='report_user'),
]
