from django import forms
from .models import Mood, Feedback, Intervention, Tag

class MoodForm(forms.ModelForm):
    """Form for logging a new mood entry"""
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add tags (comma-separated, e.g., work, home, exercise)',
            'class': 'form-input'
        }),
        help_text="Optional: Add context tags"
    )
    
    class Meta:
        model = Mood
        fields = ['emotion', 'intensity', 'note']
        widgets = {
            'emotion': forms.Select(attrs={
                'class': 'form-select'
            }),
            'intensity': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'max': '10'
            }),
            'note': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Optional: Add a brief note about what you\'re experiencing...',
                'class': 'form-textarea'
            }),
        }
    
    def save(self, commit=True):
        """Override save to handle tags"""
        instance = super().save(commit=commit)
        
        # Process tags
        tags_input = self.cleaned_data.get('tags', '')
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        
        return instance


class FeedbackForm(forms.ModelForm):
    """Form for submitting feedback on an intervention"""
    class Meta:
        model = Feedback
        fields = ['result']
        widgets = {
            'result': forms.RadioSelect()
        }


class InterventionForm(forms.ModelForm):
    """Form for submitting new interventions"""
    class Meta:
        model = Intervention
        fields = ['title', 'description', 'submitted_by']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Take 3 deep breaths',
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the intervention in detail...',
                'class': 'form-textarea'
            }),
            'submitted_by': forms.TextInput(attrs={
                'placeholder': 'Your name or alias (optional)',
                'class': 'form-input'
            }),
        }