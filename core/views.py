from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
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


def dashboard(request):
    """
    Main dashboard showing:
    - Recent mood logs
    - Mood trend chart
    - Top interventions
    """
    # Get recent moods (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_moods = Mood.objects.filter(timestamp__gte=thirty_days_ago).order_by('-timestamp')[:10]
    
    # Get mood trend data for chart (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    mood_trend = Mood.objects.filter(timestamp__gte=seven_days_ago).values('timestamp__date').annotate(
        avg_intensity=Avg('intensity')
    ).order_by('timestamp__date')
    
    # Prepare data for Chart.js
    trend_labels = [str(entry['timestamp__date']) for entry in mood_trend]
    trend_data = [float(entry['avg_intensity']) for entry in mood_trend]
    
    # Get top-rated interventions
    top_interventions = sorted(
        Intervention.objects.filter(is_active=True),
        key=lambda x: (x.get_success_score(), x.get_total_votes()),
        reverse=True
    )[:5]
    
    # Get total stats
    total_logs = Mood.objects.count()
    total_interventions = Intervention.objects.filter(is_active=True).count()
    total_feedback = Feedback.objects.count()
    
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


def log_mood(request):
    """Mood logging form with intervention suggestion"""
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            mood = form.save()
            
            # Suggest a random intervention
            interventions = list(Intervention.objects.filter(is_active=True))
            if interventions:
                suggested = random.choice(interventions)
                mood.suggested_intervention = suggested
                mood.save()
                
                # Redirect to intervention page
                return redirect('intervention_suggestion', mood_id=mood.id)
            else:
                return redirect('dashboard')
    else:
        form = MoodForm()
    
    return render(request, 'log_mood.html', {'form': form})


def intervention_suggestion(request, mood_id):
    """Show suggested intervention and collect feedback"""
    mood = get_object_or_404(Mood, id=mood_id)
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


def heatmap_view(request):
    """
    Emotional heatmap: Average mood intensity by time of day and day of week
    """
    # Get all moods
    moods = Mood.objects.all()
    
    # Create 7x24 matrix (days x hours)
    heatmap_data = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day_idx in range(7):
        day_data = []
        for hour in range(24):
            avg_intensity = moods.filter(
                timestamp__week_day=day_idx + 2,  # Django week_day: 1=Sunday, 2=Monday
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


def correlations_view(request):
    """
    Show correlations between tags and emotions/intensities
    """
    # Get all tags with mood counts
    tags = Tag.objects.annotate(mood_count=Count('mood')).filter(mood_count__gt=0)
    
    correlations = []
    for tag in tags:
        # Get average intensity for this tag
        avg_intensity = Mood.objects.filter(tags=tag).aggregate(Avg('intensity'))['intensity__avg']
        
        # Get most common emotion with this tag
        emotion_counts = Mood.objects.filter(tags=tag).values('emotion').annotate(
            count=Count('emotion')
        ).order_by('-count').first()
        
        if emotion_counts:
            correlations.append({
                'tag': tag.name,
                'avg_intensity': round(avg_intensity, 1) if avg_intensity else 0,
                'top_emotion': emotion_counts['emotion'],
                'mood_count': tag.mood_count,
            })
    
    # Sort by average intensity descending
    correlations.sort(key=lambda x: x['avg_intensity'], reverse=True)
    
    context = {
        'correlations': correlations,
    }
    
    return render(request, 'correlations.html', context)


def interventions_list(request):
    """List all interventions with success scores"""
    interventions = Intervention.objects.filter(is_active=True)
    
    # Add scores to each intervention
    interventions_with_scores = [
        {
            'intervention': i,
            'score': i.get_success_score(),
            'votes': i.get_total_votes()
        }
        for i in interventions
    ]
    
    # Sort by score then votes
    interventions_with_scores.sort(key=lambda x: (x['score'], x['votes']), reverse=True)
    
    context = {
        'interventions': interventions_with_scores,
    }
    
    return render(request, 'interventions_list.html', context)


def submit_intervention(request):
    """Form for community to submit new interventions"""
    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('interventions_list')
    else:
        form = InterventionForm()
    
    return render(request, 'submit_intervention.html', {'form': form})