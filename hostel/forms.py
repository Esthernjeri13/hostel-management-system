from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ContactInquiry, RoomBooking
from django.contrib.auth import get_user_model
from .models import Room, Student, Feedback

class SignUpForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, widget=forms.RadioSelect)
    name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True)
    student_id = forms.CharField(max_length=10, required=True, label="Student ID")
    phone = forms.CharField(max_length=15, required=True, label="Phone Number")

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'user_type', 'name', 'email', 'student_id', 'phone']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, widget=forms.RadioSelect)

class FeedbackForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, label="Your Name")
    email = forms.EmailField(required=True, label="Your Email")
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your feedback here...'
            }),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'capacity', 'beds_available', 'is_available']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'email', 'room', 'rent_paid', 'rent_due']


class RentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['rent_paid', 'rent_due']

class FeedbackManagementForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['student', 'message']


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'inquiry_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'inquiry_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 4}),
        }

class RoomBookingForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'})
    )

    class Meta:
        model = RoomBooking
        fields = ['name', 'phone', 'room_type', 'check_in_date', 'duration_of_stay', 'special_requests']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'check_in_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duration_of_stay': forms.Select(attrs={'class': 'form-control'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Special Requests (Optional)', 'rows': 3}),
        }