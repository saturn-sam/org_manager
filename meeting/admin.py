from django.contrib import admin

from .models import Meeting, Agenda, Attendance
# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id','meeting_number', 'attendee')

class AgendaAdmin(admin.ModelAdmin):
    list_display = ('meeting_number','topic')

admin.site.register(Meeting)
admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Attendance, AttendanceAdmin)