from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField



class User(AbstractUser):
    username = models.CharField(unique=True, null=True, blank=True, max_length=100)
    email = models.EmailField(unique=True, null=False)
    role = models.CharField(max_length=100, default="user")
    photo = ResizedImageField(quality=75, size = [200,200],upload_to="static/uploads/photos",null=True, blank=True)
    OTP = models.CharField(max_length = 130, null=True, blank=True)
    has_group = models.BooleanField(default = False)
    
    REQUIRED_FIELDS=['username']
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    # pass

class DeadLine(models.Model):
    deadline = models.DateField()
    academic_year = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return str(self.deadline)    

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    reciever = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    severity = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)


    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.message[0:20]
    
class Course(models.Model):
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.name    


class Group(models.Model):
    name = models.CharField(max_length=100)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="supervisor")
    leader = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="members")
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default="pending")
    academic_year = models.CharField(max_length=100)
    delayed = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null = True, blank=True)
    def __str__(self):
        return self.name


class Project(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    abstract = models.TextField()
    viewers = models.ManyToManyField(User, related_name="viewers", blank =True)
    report = models.FileField(upload_to="static/uploads/docs",null=True,blank = True)
    rating = models.DecimalField(max_digits=1, decimal_places=0, default=0)
    github_link = models.CharField(max_length=100, null=True, blank=True)
    preview_link = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, default="pending")
    date = models.DateTimeField(auto_now_add=True)
    delayed = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default = False)
    image0 =models.FileField(upload_to="static/uploads/screenshots",null=True,blank = True)
    image1 =models.FileField(upload_to="static/uploads/screenshots",null=True,blank = True)
    image2 =models.FileField(upload_to="static/uploads/screenshots",null=True,blank = True)
    image3 =models.FileField(upload_to="static/uploads/screenshots",null=True,blank = True)
    
    def __str__(self):
        return self.title 


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)       
    rating = models.DecimalField(max_digits=2, decimal_places=0) 
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.body[0:30]


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()  
    file = models.FileField(upload_to="static/uploads/messages", blank = True)  
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:20]


class Grade(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.OneToOneField(User, related_name ="student", on_delete=models.CASCADE)
    score = models.IntegerField(default = 0)
    date = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    def __str__(self):
        return self.student.email
    





