from django.contrib import admin

# Register your models here.

from .models import Mood, Intervention, Feedback, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['title', 'submitted_by', 'is_active', 'created_at', 'success_score', 'total_votes']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    
    def success_score(self, obj):
        return obj.get_success_score()
    success_score.short_description = 'Success Score'
    
    def total_votes(self, obj):
        return obj.get_total_votes()
    total_votes.short_description = 'Total Votes'

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ['emotion', 'intensity', 'timestamp', 'suggested_intervention']
    list_filter = ['emotion', 'timestamp']
    search_fields = ['note']
    filter_horizontal = ['tags']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['intervention', 'result', 'created_at']
    list_filter = ['result', 'created_at']