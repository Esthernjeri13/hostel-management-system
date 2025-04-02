"""
URL configuration for hostelmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from hostel import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rooms/', views.student_rooms, name='student_rooms'),


    path('feedback/', views.student_feedback, name='student_feedback'),
    path('contact/',views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('index/', views.index, name='index'),
    path('book/', views.book_room, name='book_room'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.my_profile, name='my_profile'),
]
