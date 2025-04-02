from django.contrib import admin
from .models import Room, Student, Feedback, CustomUser, ContactInquiry, RoomBooking, Message

# Register your models here.

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'room', 'rent_paid', 'rent_due')
    list_filter = ('room',)
    search_fields = ('name', 'student_id')
    readonly_fields = ('rent_due',)  # Rent due is calculated automatically

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'name', 'email', 'student_id', 'phone', 'room'),
        }),
        ('Rent Information', {
            'fields': ('rent_paid', 'rent_due'),
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override save_model to calculate rent due after saving."""
        obj.calculate_rent_due()
        super().save_model(request, obj, form, change)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'capacity', 'beds_available', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number',)

    def get_queryset(self, request):
        """Separate available and unavailable rooms in Django Admin."""
        qs = super().get_queryset(request)
        return qs.order_by('-is_available')  # Show available rooms first


class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'room_type', 'room', 'status')
    list_filter = ('status', 'room_type')
    actions = ['assign_room']

    def assign_room(self, request, queryset):
        """Admin action to assign a room to selected bookings."""
        for booking in queryset:
            if booking.status == 'pending':
                # Find an available room of the selected room type
                available_room = Room.objects.filter(room_type=booking.room_type, is_available=True).first()
                if available_room:
                    # Assign the room and update the booking status
                    booking.assign_room(available_room)  # Call the assign_room method
                    self.message_user(request, f"Room {available_room.room_number} assigned to {booking.student.name}.")
                else:
                    # Notify the student if no room is available
                    booking.notify_unavailability()
                    self.message_user(request, f"No available rooms for {booking.student.name}.", level='error')

    assign_room.short_description = "Assign room to selected bookings"

    def save_model(self, request, obj, form, change):
        """Override save_model to call assign_room when a room is assigned."""
        if obj.room and obj.status == 'pending':  # Check if a room is being assigned
            obj.assign_room(obj.room)  # Call the assign_room method
        super().save_model(request, obj, form, change)  # Call the parent save method



class MessageAdmin(admin.ModelAdmin):
    list_display = ('student', 'content', 'timestamp')
    list_filter = ('student',)
    search_fields = ('student__name', 'content')

admin.site.register(Room, RoomAdmin)
admin.site.register(RoomBooking, RoomBookingAdmin)
admin.site.register(CustomUser)
admin.site.register(Student, StudentAdmin)
admin.site.register(Feedback)
admin.site.register(ContactInquiry)
admin.site.register(Message, MessageAdmin)




