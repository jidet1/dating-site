from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversation_list'),
    path('conversation/<int:match_id>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('send-message/', views.SendMessageView.as_view(), name='send_message'),
]
