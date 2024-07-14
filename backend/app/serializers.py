from rest_framework.serializers import ModelSerializer, CharField
from .models import Topic, User, Notification, Project, Group, Comment, Course, Message, User,Grade, DeadLine
class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'       

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  

class GroupSerializer(ModelSerializer):
    
    class Meta:
        model = Group
        fields = '__all__'  


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    email = CharField(source = 'author.email', read_only = True, max_length =100)
    class Meta:
        model = Message
        fields = '__all__'      


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'            
class GradeSerializer(ModelSerializer):
    email = CharField(source = 'student.email', read_only = True, max_length =100)
    class Meta:
        model = Grade
        fields = '__all__'     

class DeadLineSerializer(ModelSerializer):
    class Meta:
        model = DeadLine
        fields = '__all__'    

class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'       

class AllProjectsSerializer(ModelSerializer):

    group_name = CharField(source = "group.name", read_only = True)
    course_name = CharField(source = "group.course.name", read_only = True)

    class Meta:
        model = Project
        fields = ["title", "status", "group_name", "course_name"]                 