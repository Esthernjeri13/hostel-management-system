from django.contrib import messages
# Create your views here.
from django.shortcuts import render, redirect
from .models import Room, Student, Feedback, RoomBooking, Message
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm, FeedbackForm, RoomForm, StudentForm, RentForm, ContactInquiryForm, RoomBookingForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
@login_required(login_url='/hostel/login/')
def index(request):
    return render(request, 'student/index.html', {'username': request.user.username})

def student_rooms(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'student/index.html', {'rooms': rooms})


@login_required(login_url='/hostel/login/')
def student_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            try:
                student = Student.objects.get(user=request.user)  # Get logged-in student
                # Create feedback with user, student, and message
                Feedback.objects.create(
                    user=request.user,  # Add the logged-in user
                    student=student,
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    message=form.cleaned_data['message']
                )
                messages.success(request, "Feedback submitted successfully!")
            except Student.DoesNotExist:
                messages.error(request, "You must be a registered student to submit feedback.")
        else:
            messages.error(request, "Invalid form submission. Please check your input.")

        return redirect('student_feedback')  # Redirect to prevent resubmission
    else:
        form = FeedbackForm()

    return render(request, 'student/index.html', {'form': form})
def contact(request):
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your inquiry has been submitted successfully!")
            return redirect('contact')  # Redirect to the same page or another page
    else:
        form = ContactInquiryForm()

    return render(request, 'student/index.html', {'form': form})


def book_room(request):
    # Ensure the user has a Student object (safeguard)
    if not hasattr(request.user, 'student'):
        messages.error(request, "Please complete your student profile before booking a room.")
        return redirect('signup')  # Redirect to signup if no Student object exists

    if request.method == 'POST':
        form = RoomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)  # Create booking object without saving
            booking.student = request.user.student # Link the booking to the logged-in student
            booking.status = 'pending'  # Set status to pending
            booking.save()  # Save to DB

            messages.success(request, "Your booking request has been submitted!")
            return redirect('book_room')  # Redirect to the same page to display the message
    else:
        form = RoomBookingForm()

    return render(request, 'student/book.html', {'form': form})
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.user_type = form.cleaned_data['user_type']  # Set user type from form
            user.save()  # Save the user

            # Create a Student object for the user if they are a student
            if user.user_type == 'student':
                Student.objects.create(
                    user=user,
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    student_id=form.cleaned_data['student_id'],
                    phone=form.cleaned_data['phone']
                )

            login(request, user)  # Log in the user

            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            selected_user_type = form.cleaned_data['user_type']  # Fetch user_type from form

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Ensure user_type matches the selected role (case-insensitive)
                if user.user_type.strip().lower() == selected_user_type.strip().lower():
                    login(request, user)
                    # Redirect based on user type
                    return redirect('admin_dashboard' if user.user_type.lower() == 'admin' else 'index')
                else:
                    form.add_error(None, 'Incorrect role selected for this account.')
            else:
                form.add_error(None, 'Invalid username or password.')
        else:
            form.add_error(None, 'Invalid form submission.')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})

@login_required(login_url='/hostel/login/')
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/hostel/login/')
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    return render(request, 'admin/dashboard.html')


def room_management(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    rooms = Room.objects.all()
    return render(request, 'admin/room_management.html', {'rooms': rooms})


def student_management(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    students = Student.objects.all()
    return render(request, 'admin/student_management.html', {'students': students})


def rent_management(request):
    if request.user.user_type != 'admin':
        return redirect('login')

    students = Student.objects.all()
    student_balances = []

    for student in students:
        balance = student.rent_due - student.rent_paid
        student_balances.append({
            'student': student,
            'balance': balance,
        })

    return render(request, 'admin/rent_management.html', {'student_balances': student_balances})


def feedback_management(request):
    if request.user.user_type != 'admin':
        return redirect('login')
    feedbacks = Feedback.objects.all()
    return render(request, 'admin/feedback_management.html', {'feedbacks': feedbacks})

def add_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('room_management')
    else:
        form = RoomForm()
    return render(request, 'admin/room_management.html', {'form': form})

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_management')
    else:
        form = StudentForm()
    return render(request, 'admin/student_management.html', {'form': form})

def edit_rent(request, student_id):
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        form = RentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('rent_management')
    else:
        form = RentForm(instance=student)
    return render(request, 'admin/rent_management.html', {'form': form})

def delete_feedback(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    if request.method == 'POST':
        feedback.delete()
        return redirect('feedback_management')
    return render(request, 'admin/feedback_management.html', {'feedback': feedback})
@login_required(login_url='/hostel/login/')
def my_profile(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        student = None  # Handle the case where the student profile doesn't exist
    bookings = RoomBooking.objects.filter(student=student).order_by('-booking_date')
    messages = Message.objects.filter(student=student).order_by('-timestamp')

    return render(request, 'student/profile.html', {
        'student': student,
        'bookings': bookings,
        'messages': messages,
    })