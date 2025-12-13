from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import random
import json
import csv
from django.http import HttpResponse
from django.http import JsonResponse

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
    moods = Mood.objects.filter(user=request.user)
    
    # Filter by emotion
    emotion_filter = request.GET.get('emotion')
    if emotion_filter:
        moods = moods.filter(emotion=emotion_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        moods = moods.filter(timestamp__gte=start_date)
    if end_date:
        moods = moods.filter(timestamp__lte=end_date)
    
    # Filter by tag
    tag_filter = request.GET.get('tag')
    if tag_filter:
        moods = moods.filter(tags__name=tag_filter)

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

# views.py
@login_required
def delete_mood(request, mood_id):
    mood = get_object_or_404(Mood, id=mood_id, user=request.user)
    mood.delete()
    return redirect('dashboard')

@login_required
def edit_mood(request, mood_id):
    mood = get_object_or_404(Mood, id=mood_id, user=request.user)
    if request.method == 'POST':
        form = MoodForm(request.POST, instance=mood)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = MoodForm(instance=mood)
    return render(request, 'edit_mood.html', {'form': form, 'mood': mood})


    

@login_required
def export_moods_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_moods.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Time', 'Emotion', 'Intensity', 'Tags', 'Note'])
    
    moods = Mood.objects.filter(user=request.user).order_by('-timestamp')
    for mood in moods:
        tags = ', '.join([tag.name for tag in mood.tags.all()])
        writer.writerow([
            mood.timestamp.date(),
            mood.timestamp.time().strftime('%H:%M'),
            mood.get_emotion_display(),
            mood.intensity,
            tags,
            mood.note or ''
        ])
    
    return response

@login_required
def weekly_report(request):
    week_ago = timezone.now() - timedelta(days=7)
    moods = Mood.objects.filter(user=request.user, timestamp__gte=week_ago)
    
    report = {
        'total_logs': moods.count(),
        'avg_intensity': moods.aggregate(Avg('intensity'))['intensity__avg'],
        'most_common_emotion': moods.values('emotion').annotate(
            count=Count('emotion')
        ).order_by('-count').first(),
        'peak_day': moods.values('timestamp__week_day').annotate(
            avg_intensity=Avg('intensity')
        ).order_by('-avg_intensity').first(),
        'best_day': moods.order_by('intensity').first(),
        'worst_day': moods.order_by('-intensity').first(),
    }
    
    return render(request, 'weekly_report.html', {'report': report})

@login_required
def get_streak(user):
    moods = Mood.objects.filter(user=user).order_by('-timestamp')
    if not moods:
        return 0
    
    streak = 1
    current_date = moods[0].timestamp.date()
    
    for mood in moods[1:]:
        mood_date = mood.timestamp.date()
        if (current_date - mood_date).days == 1:
            streak += 1
            current_date = mood_date
        elif (current_date - mood_date).days > 1:
            break
    
    return streak


@login_required
def comparison_view(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)
    
    this_week = Mood.objects.filter(user=request.user, timestamp__gte=week_ago)
    last_week = Mood.objects.filter(
        user=request.user, 
        timestamp__gte=two_weeks_ago,
        timestamp__lt=week_ago
    )
    
    comparison = {
        'this_week_avg': this_week.aggregate(Avg('intensity'))['intensity__avg'] or 0,
        'last_week_avg': last_week.aggregate(Avg('intensity'))['intensity__avg'] or 0,
        'this_week_count': this_week.count(),
        'last_week_count': last_week.count(),
    }
    
    # Calculate percentage change
    if comparison['last_week_avg'] > 0:
        comparison['intensity_change'] = (
            (comparison['this_week_avg'] - comparison['last_week_avg']) 
            / comparison['last_week_avg'] * 100
        )
    
    return render(request, 'comparison.html', {'comparison': comparison})

@login_required
def insights_dashboard(request):
    moods = Mood.objects.filter(user=request.user)
    
    insights = []
    
    # Insight 1: Day of week pattern
    day_stats = {}
    for day in range(7):
        day_moods = moods.filter(timestamp__week_day=day+2)
        if day_moods.exists():
            day_stats[day] = day_moods.aggregate(Avg('intensity'))['intensity__avg']
    
    if day_stats:
        worst_day = max(day_stats, key=day_stats.get)
        best_day = min(day_stats, key=day_stats.get)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        insights.append({
            'icon': '📅',
            'text': f"Your mood is typically better on {days[best_day]}s and harder on {days[worst_day]}s"
        })
    
    # Insight 2: Time of day
    morning = moods.filter(timestamp__hour__range=(6, 12)).aggregate(Avg('intensity'))
    evening = moods.filter(timestamp__hour__range=(18, 23)).aggregate(Avg('intensity'))
    
    if morning['intensity__avg'] and evening['intensity__avg']:
        if evening['intensity__avg'] < morning['intensity__avg']:
            insights.append({
                'icon': '🌙',
                'text': f"You're {((morning['intensity__avg'] - evening['intensity__avg']) / morning['intensity__avg'] * 100):.0f}% calmer in the evenings"
            })
    
    # Insight 3: Tag correlations
    tags = Tag.objects.filter(mood__user=request.user).distinct()
    tag_insights = []
    
    for tag in tags:
        with_tag = moods.filter(tags=tag).aggregate(Avg('intensity'))['intensity__avg']
        without_tag = moods.exclude(tags=tag).aggregate(Avg('intensity'))['intensity__avg']
        
        if with_tag and without_tag:
            diff = ((with_tag - without_tag) / without_tag * 100)
            if abs(diff) > 15:  # Only show significant correlations
                tag_insights.append({
                    'icon': '🏷️',
                    'text': f"#{tag.name} is associated with {abs(diff):.0f}% {'higher' if diff > 0 else 'lower'} intensity"
                })
    
    insights.extend(tag_insights[:3])  # Top 3 tag insights
    
    return render(request, 'insights_dashboard.html', {'insights': insights})




@login_required
def api_moods(request):
    moods = Mood.objects.filter(user=request.user).order_by('-timestamp')[:10]
    data = [{
        'emotion': mood.emotion,
        'intensity': mood.intensity,
        'timestamp': mood.timestamp.isoformat(),
        'tags': [tag.name for tag in mood.tags.all()]
    } for mood in moods]
    return JsonResponse({'moods': data})