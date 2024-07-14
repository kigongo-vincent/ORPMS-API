from django.contrib import admin
from .models import User, Topic, Notification, Course, Group, Project, Comment, Message, Grade, DeadLine

admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Notification)
admin.site.register(DeadLine)
admin.site.register(Group)
admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(Grade)
admin.site.register(Course)
# Register your models here.
