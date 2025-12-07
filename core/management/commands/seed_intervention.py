from django.core.management.base import BaseCommand
from core.models import Intervention

class Command(BaseCommand):
    help = 'Seeds the database with initial interventions'

    def handle(self, *args, **kwargs):
        interventions = [
            {
                'title': 'Take 3 Deep Breaths',
                'description': 'Inhale slowly through your nose for 4 counts, hold for 4, exhale through your mouth for 6. Repeat 3 times.',
                'submitted_by': 'Mental Health Community'
            },
            {
                'title': 'Drink a Glass of Water',
                'description': 'Slowly drink a full glass of water. Focus on the sensation and temperature of the water.',
                'submitted_by': 'Wellness Coach'
            },
            {
                'title': '10-Second Body Stretch',
                'description': 'Stand up and stretch your arms above your head. Hold for 10 seconds while taking deep breaths.',
                'submitted_by': 'Yoga Instructor'
            },
            {
                'title': 'Name 5 Things You Can See',
                'description': 'Ground yourself by identifying 5 things in your immediate environment. This is a grounding technique.',
                'submitted_by': 'Therapist'
            },
            {
                'title': 'Write One Sentence',
                'description': 'Write down one sentence about what you\'re feeling right now. No judgment, just observation.',
                'submitted_by': 'Journaling Expert'
            },
            {
                'title': 'Step Outside for 30 Seconds',
                'description': 'Go outside (or to a window) and feel the air on your skin for 30 seconds.',
                'submitted_by': 'Nature Therapist'
            },
            {
                'title': 'Progressive Muscle Relaxation',
                'description': 'Tense your shoulders for 5 seconds, then release. Notice the difference between tension and relaxation.',
                'submitted_by': 'Physical Therapist'
            },
            {
                'title': 'Listen to One Favorite Song',
                'description': 'Play a song that usually makes you feel good. Focus only on the music for its duration.',
                'submitted_by': 'Music Therapist'
            },
            {
                'title': 'Call a Friend',
                'description': 'Send a quick message or make a 2-minute call to someone you trust.',
                'submitted_by': 'Social Worker'
            },
            {
                'title': 'Splash Cold Water on Face',
                'description': 'Splash cold water on your face and wrists. This activates the dive reflex and can calm your nervous system.',
                'submitted_by': 'Emergency Counselor'
            },
        ]

        created_count = 0
        for intervention_data in interventions:
            intervention, created = Intervention.objects.get_or_create(
                title=intervention_data['title'],
                defaults={
                    'description': intervention_data['description'],
                    'submitted_by': intervention_data['submitted_by']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {intervention.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {intervention.title}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully seeded {created_count} new interventions!'))