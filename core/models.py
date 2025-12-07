from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Tag(models.Model):
    """Activity or location tags like #Work, #Home, #Exercise"""
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Intervention(models.Model):
    """Community-submitted micro-interventions"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.CharField(max_length=100, default="Community")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def get_success_score(self):
        """
        Calculate community success score between -1.0 and 1.0
        Formula: (helped - worse) / total_votes
        """
        feedbacks = self.feedback_set.all()
        if not feedbacks.exists():
            return 0.0
        
        helped = feedbacks.filter(result='helped').count()
        no_change = feedbacks.filter(result='no_change').count()
        worse = feedbacks.filter(result='worse').count()
        total = helped + no_change + worse
        
        if total == 0:
            return 0.0
        
        score = (helped - worse) / total
        return round(score, 2)
    
    def get_total_votes(self):
        """Get total number of feedback votes"""
        return self.feedback_set.count()
    
    class Meta:
        ordering = ['-created_at']


class Mood(models.Model):
    """Individual mood log entries - NOW WITH USER"""
    EMOTION_CHOICES = [
        ('joy', 'Joy'),
        ('sadness', 'Sadness'),
        ('anxiety', 'Anxiety'),
        ('anger', 'Anger'),
        ('fear', 'Fear'),
        ('disgust', 'Disgust'),
        ('surprise', 'Surprise'),
        ('neutral', 'Neutral'),
        ('excited', 'Excited'),
        ('calm', 'Calm'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # NEW: Link to user
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    intensity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rate intensity from 1 (low) to 10 (high)"
    )
    note = models.TextField(blank=True, null=True, max_length=500)
    tags = models.ManyToManyField(Tag, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    suggested_intervention = models.ForeignKey(
        Intervention, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='mood_logs'
    )
    
    def __str__(self):
        return f"{self.emotion} ({self.intensity}) at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def get_time_of_day(self):
        """Returns hour of day (0-23)"""
        return self.timestamp.hour
    
    def get_day_of_week(self):
        """Returns day of week (0=Monday, 6=Sunday)"""
        return self.timestamp.weekday()
    
    class Meta:
        ordering = ['-timestamp']


class Feedback(models.Model):
    """User feedback on intervention effectiveness"""
    RESULT_CHOICES = [
        ('helped', 'Helped'),
        ('no_change', 'No Change'),
        ('worse', 'Made it Worse'),
    ]
    
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.intervention.title} - {self.result}"
    
    class Meta:
        ordering = ['-created_at']