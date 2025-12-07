from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Auth URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app URLs (require login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log/', views.log_mood, name='log_mood'),
    path('intervention/<int:mood_id>/', views.intervention_suggestion, name='intervention_suggestion'),
    path('heatmap/', views.heatmap_view, name='heatmap'),
    path('correlations/', views.correlations_view, name='correlations'),
    
    # Public intervention pages
    path('interventions/', views.interventions_list, name='interventions_list'),
    path('interventions/submit/', views.submit_intervention, name='submit_intervention'),
]