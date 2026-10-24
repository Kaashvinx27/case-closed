from django.urls import path
from . import views

urlpatterns = [
    # Main Navigation Pages
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cases/', views.cases_list, name='cases_list'),
    path('cases/<slug:case_slug>/', views.case_briefing, name='case_briefing'),
    path('investigate/<slug:case_slug>/', views.investigation_workspace, name='investigation'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('profile/', views.profile_view, name='profile'),
    path('how-to-play/', views.how_to_play, name='how_to_play'),

    # Authentication
    path('login/', views.detective_login, name='login'),
    path('register/', views.detective_register, name='register'),
    path('logout/', views.detective_logout, name='logout'),

    # Asynchronous AJAX / JSON APIs
    path('api/investigate/<slug:case_slug>/discover/', views.api_discover_evidence, name='api_discover_evidence'),
    path('api/investigate/<slug:case_slug>/evidence/<int:evidence_id>/', views.api_get_evidence_detail, name='api_get_evidence_detail'),
    path('api/investigate/<slug:case_slug>/interview/', views.api_interview_suspect, name='api_interview_suspect'),
    path('api/investigate/<slug:case_slug>/hint/', views.api_request_hint, name='api_request_hint'),
    path('api/investigate/<slug:case_slug>/note/', views.api_save_note, name='api_save_note'),
    path('api/investigate/<slug:case_slug>/connect/', views.api_connect_board, name='api_connect_board'),
    path('api/investigate/<slug:case_slug>/disconnect/', views.api_disconnect_board, name='api_disconnect_board'),
    path('api/investigate/<slug:case_slug>/accuse/', views.api_submit_accusation, name='api_submit_accusation'),
    path('api/investigate/<slug:case_slug>/state/', views.api_get_session_state, name='api_get_session_state'),
]
