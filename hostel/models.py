from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    student: 'Student'
    def __str__(self):
        return self.username


class Room(models.Model):
    # Define room types and their fixed rent prices
    ROOM_TYPE_CHOICES = [
        ('single', 'Single Room - 10,000'),
        ('studio', 'Studio Room - 12,000'),
        ('4_sharing', '4 Sharing - 8,500'),
        ('twin', 'Twin Room - 9,500'),
        ('6_sharing', '6 Sharing - 7,500'),
        ('8_sharing', '8 Sharing - 6,500'),
    ]

    # Room fields
    room_number = models.CharField(max_length=10, unique=True)  # Unique room identifier
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)  # Type of room
    capacity = models.IntegerField(default=1)  # Total beds in the room
    beds_available = models.IntegerField(default=1)  # Beds left
    is_available = models.BooleanField(default=True)  # Availability status

    @property
    def rent_price(self):
        """Return the fixed rent price based on the room type."""
        prices = {
            'single': 10000,
            'studio': 12000,
            '4_sharing': 8500,
            'twin': 9500,
            '6_sharing': 7500,
            '8_sharing': 6500,
        }
        return prices.get(self.room_type, 0)  # Default to 0 if room type is invalid

    def update_availability(self):
        """Update room availability based on available beds."""
        self.is_available = self.beds_available > 0


    def save(self, *args, **kwargs):
        """
        Override the save method to ensure availability is updated whenever the room is saved.
        """
        self.update_availability()  # Update availability before saving
        super().save(*args, **kwargs)  # Call the parent save method

    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()} ({self.beds_available} beds left)"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    student_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True)
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True)
    rent_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rent_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_rent_due(self):
        """Calculate rent due based on the room's fixed price."""
        if self.room:
            self.rent_due = self.room.rent_price - self.rent_paid


    def save(self, *args, **kwargs):
        """Override save method to update rent due whenever the student is saved."""
        self.calculate_rent_due()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)  # New field
    email = models.EmailField(null=True, blank=True)  # New field
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.student.name}"

class ContactInquiry(models.Model):
    INQUIRY_CHOICES = [
        ('room_booking', 'Room Booking'),
        ('rent_payment', 'Rent Payment'),
        ('maintenance', 'Maintenance Request'),
        ('general', 'General Inquiry'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, unique=True, null=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_CHOICES)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.inquiry_type}"

class RoomBooking(models.Model):
    ROOM_CHOICES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('shared', 'Shared Room'),
    ]
    DURATION_CHOICES = [
        ('one_month', 'One Month'),
        ('one_semester', 'One Semester'),
        ('one_year', 'One Year'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Room Assignment Complete'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE)  # Changed back to FK for better tracking
    phone = models.CharField(max_length=15, unique=True, null=True)
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, blank=True, null=True)
    room_type = models.CharField(max_length=10, choices=ROOM_CHOICES)
    check_in_date = models.DateField()
    duration_of_stay = models.CharField(max_length=20, choices=DURATION_CHOICES)
    special_requests = models.TextField(blank=True, null=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')


    def assign_room(self, room):
        """Assign a room, update status, and notify the student."""
        if room and room.beds_available > 0:
            self.room = room
            self.status = 'assigned'
            room.beds_available -= 1
            room.update_availability()  # Update availability
            room.save()  # Save the room after updating
            self.save()  # Save the booking after assigning the room
            Message.objects.create(
                student=self.student,
                content=f"Your room assignment is complete! You have been assigned Room {room.room_number}."
            )

    def notify_unavailability(self):
        """Send a message if room request is denied."""
        Message.objects.create(
            student=self.student,
            content="Unfortunately, the room you requested is unavailable. Please select another room."
        )

    def __str__(self):
        return f"{self.student.name} - {self.get_status_display()}"

class Message(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message for {self.student.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"