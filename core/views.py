from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import random
import json

from .models import Mood, Intervention, Feedback, Tag
from .forms import MoodForm, FeedbackForm, InterventionForm


def home(request):
    """Landing page"""
    return render(request, 'home.html')


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('home')



    
@login_required
def dashboard(request):
    """
    Main dashboard showing ONLY current user's data
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_moods = Mood.objects.filter(
        user=request.user,
        timestamp__gte=thirty_days_ago
    ).order_by('-timestamp')[:10]
    
    # Mood trend for current user only
    seven_days_ago = timezone.now() - timedelta(days=7)
    mood_trend = Mood.objects.filter(
        user=request.user,
        timestamp__gte=seven_days_ago
    ).values('timestamp__date').annotate(
        avg_intensity=Avg('intensity')
    ).order_by('timestamp__date')
    
    # Convert to lists for JSON
    trend_labels = []
    trend_data = []
    for entry in mood_trend:
        trend_labels.append(str(entry['timestamp__date']))
        if entry['avg_intensity']:
            trend_data.append(float(entry['avg_intensity']))
        else:
            trend_data.append(0)
    
    # Top interventions (community-wide)
    top_interventions = sorted(
        Intervention.objects.filter(is_active=True),
        key=lambda x: (x.get_success_score(), x.get_total_votes()),
        reverse=True
    )[:5]
    
    # User's stats
    total_logs = Mood.objects.filter(user=request.user).count()
    total_interventions = Intervention.objects.filter(is_active=True).count()
    total_feedback = Feedback.objects.filter(mood__user=request.user).count()
    
    context = {
        'recent_moods': recent_moods,
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
        'top_interventions': top_interventions,
        'total_logs': total_logs,
        'total_interventions': total_interventions,
        'total_feedback': total_feedback,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def log_mood(request):
    """Mood logging form - saves to current user"""
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            mood = form.save(commit=False)
            mood.user = request.user  # Assign to current user
            mood.save()
            form.save_m2m()  # Save tags
            
            # Suggest intervention
            interventions = list(Intervention.objects.filter(is_active=True))
            if interventions:
                suggested = random.choice(interventions)
                mood.suggested_intervention = suggested
                mood.save()
                return redirect('intervention_suggestion', mood_id=mood.id)
            else:
                return redirect('dashboard')
    else:
        form = MoodForm()
    
    return render(request, 'log_mood.html', {'form': form})


@login_required
def intervention_suggestion(request, mood_id):
    """Show suggested intervention"""
    mood = get_object_or_404(Mood, id=mood_id, user=request.user)
    intervention = mood.suggested_intervention
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.mood = mood
            feedback.intervention = intervention
            feedback.save()
            return redirect('dashboard')
    else:
        form = FeedbackForm()
    
    context = {
        'mood': mood,
        'intervention': intervention,
        'form': form,
    }
    
    return render(request, 'intervention_suggestion.html', context)


@login_required
def heatmap_view(request):
    """Heatmap for current user only"""
    moods = Mood.objects.filter(user=request.user)
    
    heatmap_data = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day_idx in range(7):
        day_data = []
        for hour in range(24):
            avg_intensity = moods.filter(
                timestamp__week_day=day_idx + 2,
                timestamp__hour=hour
            ).aggregate(Avg('intensity'))['intensity__avg']
            
            day_data.append(round(avg_intensity, 1) if avg_intensity else 0)
        
        heatmap_data.append({
            'day': days[day_idx],
            'data': day_data
        })
    
    context = {
        'heatmap_data': json.dumps(heatmap_data),
        'hours': list(range(24)),
    }
    
    return render(request, 'heatmap.html', context)


@login_required
def correlations_view(request):
    """Correlations for current user only"""
    tags = Tag.objects.filter(
        mood__user=request.user
    ).annotate(mood_count=Count('mood')).filter(mood_count__gt=0).distinct()
    
    correlations = []
    for tag in tags:
        avg_intensity = Mood.objects.filter(
            user=request.user,
            tags=tag
        ).aggregate(Avg('intensity'))['intensity__avg']
        
        emotion_counts = Mood.objects.filter(
            user=request.user,
            tags=tag
        ).values('emotion').annotate(
            count=Count('emotion')
        ).order_by('-count').first()
        
        if emotion_counts:
            correlations.append({
                'tag': tag.name,
                'avg_intensity': round(avg_intensity, 1) if avg_intensity else 0,
                'top_emotion': emotion_counts['emotion'],
                'mood_count': Mood.objects.filter(user=request.user, tags=tag).count(),
            })
    
    correlations.sort(key=lambda x: x['avg_intensity'], reverse=True)
    
    context = {
        'correlations': correlations,
    }
    
    return render(request, 'correlations.html', context)


def interventions_list(request):
    """List all interventions - public view"""
    interventions = Intervention.objects.filter(is_active=True)
    
    interventions_with_scores = [
        {
            'intervention': i,
            'score': i.get_success_score(),
            'votes': i.get_total_votes()
        }
        for i in interventions
    ]
    
    interventions_with_scores.sort(key=lambda x: (x['score'], x['votes']), reverse=True)
    
    context = {
        'interventions': interventions_with_scores,
    }
    
    return render(request, 'interventions_list.html', context)


@login_required
def submit_intervention(request):
    """Submit new intervention - requires login"""
    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('interventions_list')
    else:
        form = InterventionForm()
    
    return render(request, 'submit_intervention.html', {'form': form})