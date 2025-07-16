from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    path('swipe/', views.SwipeView.as_view(), name='swipe'),
    path('matches/', views.MatchesView.as_view(), name='matches'),
    path('like/<int:user_id>/', views.LikeUserView.as_view(), name='like_user'),
    path('pass/<int:user_id>/', views.PassUserView.as_view(), name='pass_user'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    path('unmatch/<int:user_id>/', views.UnmatchView.as_view(), name='unmatch_user'),
]
