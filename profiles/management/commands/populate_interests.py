from django.core.management.base import BaseCommand
from profiles.models import Interest

class Command(BaseCommand):
    help = 'Populate database with sample interests'

    def handle(self, *args, **options):
        interests = [
            'Travel', 'Photography', 'Cooking', 'Music', 'Movies', 'Reading',
            'Sports', 'Fitness', 'Art', 'Dancing', 'Hiking', 'Gaming',
            'Technology', 'Fashion', 'Food', 'Wine', 'Coffee', 'Yoga',
            'Meditation', 'Writing', 'Painting', 'Swimming', 'Running',
            'Cycling', 'Rock Climbing', 'Skiing', 'Surfing', 'Fishing',
            'Gardening', 'DIY', 'Volunteering', 'Animals', 'Nature',
            'Science', 'History', 'Politics', 'Business', 'Entrepreneurship',
            'Learning', 'Teaching', 'Comedy', 'Theater', 'Concerts',
            'Festivals', 'Shopping', 'Interior Design', 'Architecture'
        ]
        
        for interest_name in interests:
            interest, created = Interest.objects.get_or_create(name=interest_name)
            if created:
                self.stdout.write(f'Created interest: {interest_name}')
            else:
                self.stdout.write(f'Interest already exists: {interest_name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated interests'))
