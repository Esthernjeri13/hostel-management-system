from django.core.management.base import BaseCommand
from django.utils import timezone
from hostel.models import Student, Message

class Command(BaseCommand):
    help = 'Sends rent reminders to students with outstanding rent'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        if today.day == 30:  # Check if it's the 30th of the month
            students = Student.objects.filter(rent_due__gt=0)  # Find students with rent due
            for student in students:
                Message.objects.create(
                    student=student,
                    content=f"Reminder: You have an outstanding rent balance of {student.rent_due}. Please complete your payment."
                )
            self.stdout.write(self.style.SUCCESS('Rent reminders sent successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Today is not the 30th. No reminders sent.'))