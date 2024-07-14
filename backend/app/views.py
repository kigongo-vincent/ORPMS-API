from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Topic, User, Notification, Project, Group, Comment, Message, Grade, DeadLine, Course
from .serializers import TopicSerializer, UserSerializer, NotificationSerializer, ProjectSerializer, GroupSerializer, CommentSerializer, MessageSerializer, UserSerializer, GradeSerializer, DeadLineSerializer, CourseSerializer, AllProjectsSerializer
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.core.mail import send_mail
from django.http import JsonResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token payload
        token['role'] = user.role
        token['email'] = user.email
        token['has_group'] = user.has_group
        token['photo_url'] = str(user.photo) if user.photo else None

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['GET','POST'])
def topics(request):

    topics = Topic.objects.all()
    converted = TopicSerializer(topics, many=True)

    try:
        user = User.objects.get(id = request.user.id)
        is_allowed = user.role == "cordinator"
    except:
        is_allowed = False     

    if request.method == "POST" and is_allowed:
        try:
            converted = TopicSerializer(data = request.data)
            if converted.is_valid():
                converted.save()
                return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status= status.HTTP_400_BAD_REQUEST)        

    return Response(converted.data)


@api_view(["POST"])
def sign_up(request):
    try:
        if request.method == "POST":

            request.data["password"] = make_password(request.data["password"])
            request.data["OTP"] = request.data["password"][-7:-1] 
            request.data["is_active"] = False

            if "students.mak.ac.ug" in request.data["email"]:
                request.data["role"] = "student"

            elif "cit.mak.ac.ug" in request.data["email"]:
                request.data["role"] = "lecturer"
    
            try:
                user = User.objects.get(email = request.data["email"])
            except:    
                user = None

            if user:
                return Response(status= status.HTTP_406_NOT_ACCEPTABLE)

            converted = UserSerializer(data = request.data)

            if converted.is_valid():
                new_user = converted.save()

                try:
                    subject = 'ACCOUNT CREATION ON ORPMS'
                    message = f'''
Dear {request.data['email'].split('@')[0].split('.')[0]},

Thank you for choosing the Online Research-Project Management System (ORPMS) for managing research projects. We are excited to have you on board!

Your verification code for logging into the ORPMS is:

Verification Code: {request.data["OTP"]}

Please keep this code secure and do not share it with anyone. It is essential for verifying your identity and ensuring the security of your account.

We understand the importance of safeguarding your property information, and we have implemented robust security measures to protect your data. If you have any questions or concerns regarding the security of our platform, please don't hesitate to reach out to us.

Once again, welcome to ORPMS! We look forward to providing you with a seamless property management experience.

Best regards,
The ORPMS Team
'''
                    email_from = 'ORPMS TEAM'
                    recipient_list = [request.data["email"]]

                    send_mail(subject, message, email_from, recipient_list)
                except:
                    pass
                    # return Response(status= status.HTTP_400_BAD_REQUEST)        


                return Response(converted.data, status=status.HTTP_201_CREATED)
    except:
        return Response(status= status.HTTP_400_BAD_REQUEST)        


@api_view(['GET', 'POST'])
def notifications(request, pk):
    notifications = Notification.objects.filter(reciever = str(pk))
    converted = NotificationSerializer(notifications, many=True)

    if request.method == "POST":
        serialized = NotificationSerializer(data = request.data)

        if serialized.is_valid():
            serialized.save()
            return Response(converted.data, status=status.HTTP_201_CREATED)

    return Response(converted.data)

@api_view(['GET','POST'])
def external_notifications(request):
        serialized = NotificationSerializer(data = request.data)

        if serialized.is_valid():
            serialized.save()
            return Response(serialized.data, status=status.HTTP_201_CREATED)
        return Response({"message": "this endpoint supports posting only"})

@api_view(['GET'])
def notification(request, pk):
    notifications = Notification.objects.filter(reciever = pk)
    for notification in notifications:
        notification.is_viewed = True
        notification.save()
    converted = NotificationSerializer(notifications, many=True)
    return Response(converted.data)


@api_view(['GET'])
def search(request,pk):
    projects = Project.objects.filter(
        
        Q(topic__name__icontains = pk) |
        Q(group__course__name__icontains = pk) |
        Q(title__icontains = pk) |
        Q(abstract__icontains = pk) |
        Q(github_link__icontains = pk) |
        Q(preview_link__icontains = pk) |
        Q(date__icontains = pk) |
        Q(group__name__icontains = pk) |
        Q(group__date__icontains = pk) |
        Q(group__leader__email__icontains = pk) |
        Q(group__supervisor__email__icontains = pk) 
    )
    converted = ProjectSerializer(projects, many = True)
    return Response(converted.data)

@api_view(['POST'])
def add_project(request):
    try:
        converted = ProjectSerializer(data = request.data)
        if converted.is_valid():
            converted.save()
            return Response(converted.data,status=status.HTTP_201_CREATED)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)    


@api_view(['GET'])
def projects(request,category, pk):
    try:
        if category == "topic":
            projects = Project.objects.filter(topic__name = pk)
            converted = ProjectSerializer(projects, many = True)
            return Response(converted.data)   
        elif category == "year":
            projects = Project.objects.filter(date__icontains = pk)
            converted = ProjectSerializer(projects, many = True)
            return Response(converted.data)    
        elif category == "supervisor":
            projects = Project.objects.filter(group__supervisor = pk)
            converted = ProjectSerializer(projects, many = True)
            return Response(converted.data)    
    except:    
        return Response(status = status.HTTP_400_BAD_REQUEST)    



@api_view(['POST'])    
def add_group(request):           
    converted = GroupSerializer(data = request.data)
    groups = Group.objects.all().count()
    request.data["name"] = f"Group {groups+1}"
    if converted.is_valid():

        leader = User.objects.get(id = request.data["leader"])
        leader.has_group = True
        leader.save()

        members = request.data["members"]
        new_group = converted.save()

        for member in members:
            group_member = User.objects.get(id = member)
            group_member.has_group = True
            group_member.group_number = new_group.id
            group_member.save()

        return Response(converted.data, status=status.HTTP_201_CREATED)
    else:
        return Response(status= status.HTTP_400_BAD_REQUEST)        


@api_view(['GET', 'POST'])
def groups(request, pk):
    groups = Group.objects.filter(supervisor = pk)
    converted = GroupSerializer(groups, many=True)
    return Response(converted.data)

@api_view(['GET']) 
def project(request, pk):
    try:
        project = Project.objects.get(id =pk)
        converted = ProjectSerializer(project)
    except:
        return Response(status = status.HTTP_404_NOT_FOUND)
    return Response(converted.data)  

@api_view(['GET', 'POST'])
def comments(request, pk):
    comments = Comment.objects.filter(project = pk)
    converted = CommentSerializer(comments, many = True)

    if request.method == "POST":
        converted = CommentSerializer(data = request.data)
        if converted.is_valid():
            converted.save()
            return Response(converted.data, status=status.HTTP_201_CREATED)
    return Response(converted.data)


@api_view(['GET', 'POST'])
def messages(request,pk):
        messages = Message.objects.filter(group=pk)
        all_messages = MessageSerializer(messages, many=True)

        if request.method == "POST":
            converted = MessageSerializer(data = request.data)
            if converted.is_valid():
                converted.save()
                return Response(all_messages.data, status=status.HTTP_201_CREATED)
        
        return Response(all_messages.data)
                

@api_view(['GET'])
def user(request,pk):
    try:
        user = User.objects.get(id=pk)
        converted = UserSerializer(user)
        return Response(converted.data)
    except:
        return Response(status = status.HTTP_404_NOT_FOUND)    


@api_view(['GET'])
def group(request, pk):
    try:
        project = Project.objects.get(id = pk)

        group = Group.objects.get(id = project.group.id)
        
        deadline = DeadLine.objects.get(academic_year = group.academic_year)

        converted = GroupSerializer(group)

        new_data = converted.data

        new_data['deadline'] = deadline.deadline

        return Response(new_data)
    
    except:
        return Response(status = status.HTTP_404_NOT_FOUND)    


@api_view(['GET'])
def group_info(request, pk):
    try:
        group = Group.objects.get(id = pk)
        converted = GroupSerializer(group)
        return Response(converted.data)
    except:
        return Response(status = status.HTTP_404_NOT_FOUND)    

@api_view(['GET'])
def supervisors(request):
    supervisors_array = User.objects.filter(role="lecturer").values()
    supervisors_array = [ {"id": s["id"], "email": s["email"], "number_of_groups":  Group.objects.filter(supervisor = s["id"]).count() } for s in supervisors_array]
    return JsonResponse(supervisors_array, safe=False)

@api_view(['GET'])
def students(request):
    students = User.objects.filter(role="student", has_group=False)
    converted = UserSerializer(students, many = True)
    return Response(converted.data)  


@api_view(['GET'])
def get_group(request, pk):
    try:
        group = Group.objects.get(members =pk )
        converted = GroupSerializer(group)
        return Response(converted.data)
    except:
        return Response(status = status.HTTP_404_NOT_FOUND)    


@api_view(['GET'])
def get_project(request, pk):
    try:
        project = Project.objects.get(group = pk)
        converted = ProjectSerializer(project)
        return Response(converted.data)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)     


@api_view(['GET', 'PATCH'])
def update_user(request, pk):
    try:
        user = User.objects.get(id =pk)
        if request.method == "PATCH":
            converted = UserSerializer(user, data = request.data, partial = True)
            if converted.is_valid():
                converted.save()
                return Response(converted.data, status = status.HTTP_201_CREATED)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)     
    
@api_view(['PATCH'])
def approve_project(request, pk):
        project = Project.objects.get(id =pk)
        # is_allowed = request.user == project.group.supervisor
        is_allowed = True
        if is_allowed == False:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        try:        
            converted = ProjectSerializer(project, data = request.data, partial = True)
            group = project.group
            group.status = "approved"
            if request.data["delayed"] == "True":
                group.delayed = True   
            group.save()
            if converted.is_valid():
                converted.save()
                return Response(converted.data, status = status.HTTP_201_CREATED)  
        except:
            return Response(status = status.HTTP_400_BAD_REQUEST)     

                

@api_view(['GET', 'PATCH'])
def update_project(request, pk):
    try:
        project = Project.objects.get(id =pk)
        if request.method == "PATCH":
 
                converted = ProjectSerializer(project, data = request.data, partial = True)
                if converted.is_valid():
                    converted.save()
                    return Response(converted.data, status = status.HTTP_201_CREATED)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)    



@api_view(['POST'])
def verify_otp(request):
    if request.method == "POST":
        try:
            OTP = request.data["OTP"]
            user = User.objects.get(OTP = OTP)
            user.is_active = True
            user.OTP = ""
            user.save()
            access_token = AccessToken.for_user(user,)
            refresh_token = RefreshToken.for_user(user)
            return Response({"access": str(access_token), "refresh": str(refresh_token), "user": {
                "email": user.email,
                "has_group": user.has_group,
                "role": user.role
            }})
        except:
            return Response(status = status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def resend(request, pk):
    try:
        user = User.objects.get(email = pk)
        if len(user.OTP) != 0:
            subject = 'ACCOUNT CREATION ON ORPMS'
            email_from = 'ORPMS TEAM'
            recipient_list = [user.email]
            message = f'''
Dear {user.email.split('@')[0].split('.')[0]},

Thank you for choosing the Online Research-Project Management System (ORPMS) for managing research projects. We are excited to have you on board!

Your verification code for logging into the ORPMS is:

Verification Code: {user.OTP}

Please keep this code secure and do not share it with anyone. It is essential for verifying your identity and ensuring the security of your account.

We understand the importance of safeguarding your property information, and we have implemented robust security measures to protect your data. If you have any questions or concerns regarding the security of our platform, please don't hesitate to reach out to us.

Once again, welcome to ORPMS! We look forward to providing you with a seamless property management experience.

Best regards,
The ORPMS Team
'''


            send_mail(subject, message, email_from, recipient_list)
            return Response(status = status.HTTP_201_CREATED)
        else:
            return Response(status = status.HTTP_403_FORBIDDEN)   

    except:
        return Response(status = status.HTTP_403_FORBIDDEN)   

@api_view(['GET'])
def years_and_supervisors(request):
    dates = Project.objects.all().values_list('date', flat = True)
    supervisors = Project.objects.filter(approved = True, status = "approved").values_list('group__supervisor', flat = True)
    unique_supervisors = list(set(supervisors))
    years = list(set([str(date.year) for date in dates ]))
    return Response({
        "years": years,
        "supervisors": unique_supervisors
    })  

@api_view(['GET'])
def years_and_supervisors(request):
    dates = Project.objects.filter(approved = True, status = "approved").values_list('date', flat = True)
    supervisors = Project.objects.filter(approved = True, status = "approved").values_list('group__supervisor', flat = True)
    unique_supervisors = list(set(supervisors))
    years = list(set([str(date.year) for date in dates ]))
    return Response({
        "years": years,
        "supervisors": unique_supervisors
    })       


@api_view(['GET'])
def add_view(request,user_id, project_id):
    try:
        project = Project.objects.get(id =project_id)
        project.viewers.add(user_id)
        return Response(status = status.HTTP_201_CREATED)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def grades(request,pk):
    try:
        marks = Grade.objects.filter(group = pk)
        converted = GradeSerializer(marks, many = True)
        return Response(converted.data)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def change_grades(request,pk):
    try:
        record= Grade.objects.get(id =pk)
        converted = GradeSerializer(record, data = request.data ,partial= True)
        if converted.is_valid():
            converted.save()
            return Response(converted.data, status = status.HTTP_201_CREATED)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def add_grade(request):
    try:
        if request.method == "POST":
            serialized = GradeSerializer(data = request.data)
            if serialized.is_valid():
                serialized.save()
                return Response(serialized.data, status = status.HTTP_201_CREATED)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)

    return Response({"message": "GET requests not allowed here"})



@api_view(['POST', 'GET'])
def deadline(request):
 
    try:
        
        deadlines = DeadLine.objects.all()
        converted = DeadLineSerializer(deadlines, many=True)

        if request.method == "POST":
            try:
                user = User.objects.get(id = request.user.id)
                is_allowed = user.role == "cordinator"
            except:
                is_allowed = False
            serialized = DeadLineSerializer(data = request.data)
            if serialized.is_valid() and is_allowed:
                serialized.save()
                return Response(converted.data, status = status.HTTP_201_CREATED)
            

        return Response(converted.data)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
def edit_deadline(request, pk):
    try:
        user = User.objects.get(id = request.user.id)
        is_allowed = user.role == "cordinator"
    except:
        is_allowed = False    
    try:
        if request.method == "PATCH" and is_allowed:
            all_deadlines = DeadLine.objects.all()
            serialized = DeadLineSerializer(all_deadlines, many = True)
            deadline = DeadLine.objects.get(id = pk)
            converted = DeadLineSerializer(deadline, data=request.data, partial = True)
            if converted.is_valid():
                converted.save()
                return Response(serialized.data, status= status.HTTP_202_ACCEPTED)
            else:
                return Response(status = status.HTTP_400_BAD_REQUEST)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST)


# func that returns reports for groups supervised by a given lecturer 
@api_view(['GET'])
def report_statistics(request, lecturer_id):
    try:

        # fetch all projects that belong to a lecturer 
        all_projects = Project.objects.filter(group__supervisor = lecturer_id)

        #fetch only projects that are approved
        approved_projects = Project.objects.filter(group__supervisor = lecturer_id, status = "approved")

        #fetch only projects that are pending
        pending_projects = Project.objects.filter(group__supervisor = lecturer_id, status = "pending")

        #fetch only projects that are approved but also delayed
        delayed_projects = Project.objects.filter(group__supervisor = lecturer_id, status = "approved", group__delayed = True)

        #send back results to client
        return Response(
            {
                "all": int(all_projects.count()),
                "approved": int(approved_projects.count()),
                "pending": int(pending_projects.count()),
                "delayed": int(delayed_projects.count())
            }
            )
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST) #incase something goes wrong



@api_view(['GET'])
def report_analysis(request):
    try:
        published_reports = Project.objects.filter(approved = True, status = "approved").count()
        delayed = Project.objects.filter(approved = True, status = "approved", delayed = True).count()
        pending_projects = Project.objects.filter(status = "pending").count()
        uploaded_reports = Project.objects.all().count()
        groups = Group.objects.all().count()
        students = User.objects.filter(role = "student",).count()
        lecturers = User.objects.filter(role = "lecturer").count()
        free_students = User.objects.filter(role = "student", has_group = False).count()
        results = {
            "published": published_reports,
            "delayed": delayed,
            "ongoing" : pending_projects,
            "uploads": uploaded_reports,
            "groups": groups,
            "students": students,
            "lecturers": lecturers,
            "free_students": free_students
        }

        return Response(results)
    except:
        return Response(status = status.HTTP_400_BAD_REQUEST) #incase something goes wrong\
    

@api_view(['POST'])
def add_member(request, pk):
        try:
            group = Group.objects.get(id = pk)
        except:
            group = None

        if group is not None:
            # is_allowed = group.supervisor.id == request.user.id
            is_allowed = True

            if is_allowed:
                newMember = User.objects.get(id = int(request.data["new_member"]))
                newMember.has_group = True

                group.members.add(request.data["new_member"])        
                Grade.objects.create(
                    student = newMember,
                    group = group
                )
                group.save()
                newMember.save()

                return Response(status=status.HTTP_202_ACCEPTED)
            
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)              

        else:
            return Response(status=status.HTTP_412_PRECONDITION_FAILED)     
                 
@api_view(['POST'])
def remove_member(request, pk):
        
        print(str(request))
        try:
            group = Group.objects.get(id = pk)
        except:
            group = None

        if group is not None:

            # is_allowed = group.supervisor.id == request.user.id

            is_allowed = True

            if is_allowed:
                newMember = User.objects.get(id = int(request.data["member"]))
                newMember.has_group = False
                newMember.save()
                group.members.remove(request.data["member"])   
                Grade.objects.get(student = newMember.id).delete()
                Message.objects.filter(author = newMember.id, group = group.id).delete()
                group.save()

                return Response(status=status.HTTP_202_ACCEPTED)
            
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)              

        else:
            return Response(status=status.HTTP_412_PRECONDITION_FAILED) 


@api_view(['GET', 'POST'])
def courses(request):
    courses = Course.objects.all()
    converted = CourseSerializer(courses, many = True)
    if request.method == "POST":
        converted = CourseSerializer(data=request.data)

        if converted.is_valid():
            converted.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    return Response(converted.data)                     
        

@api_view(['GET', 'POST'])
def all_supervisors(request):

    if request.method == "POST":
        converted = UserSerializer(data = request.data)

        if converted.is_valid():
            converted.save()
            return Response(converted.data, status= status.HTTP_201_CREATED)
        
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    supervisors = User.objects.filter(role="lecturer")
    converted = UserSerializer(supervisors, many = True)
    return Response(converted.data)


import random

@api_view(['POST'])
def OTP(request):
    try:
        if request.method == "POST":

            request.data["password"] = make_password(request.data["password"])
            request.data["OTP"] = random.randint(100000,999999)

            if "cit.mak.ac.ug" in request.data["email"]:
                pass
    
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            

            try:
                user = User.objects.get(email = request.data["email"])
            except:    
                return Response(status=status.HTTP_403_FORBIDDEN)
            

            if user:
                user.OTP = request.data["OTP"]
                user.save()
                return Response(status=status.HTTP_201_CREATED)


            try:
                subject = 'ACCOUNT CREATION ON ORPMS'
                message = f'''
                Dear {request.data['email'].split('@')[0].split('.')[0]},

                Thank you for choosing the Online Research-Project Management System (ORPMS) for managing research projects. We are excited to have you on board!

                Your verification code for logging into the ORPMS is:

                Verification Code: {request.data["OTP"]}

                Please keep this code secure and do not share it with anyone. It is essential for verifying your identity and ensuring the security of your account.

                We understand the importance of safeguarding your property information, and we have implemented robust security measures to protect your data. If you have any questions or concerns regarding the security of our platform, please don't hesitate to reach out to us.

                Once again, welcome to ORPMS! We look forward to providing you with a seamless property management experience.

                Best regards,
                The ORPMS Team
'''
                email_from = 'ORPMS TEAM'
                recipient_list = [request.data["email"]]

                send_mail(subject, message, email_from, recipient_list)

            except:
                pass
                return Response(status= status.HTTP_400_BAD_REQUEST)   
                                
    except:
        return Response(status= status.HTTP_400_BAD_REQUEST)    



@api_view(['POST'])
def verification(request):
    if request.method == "POST":
        try:
            OTP = request.data["OTP"]
            user = User.objects.get(OTP = OTP)
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            user.OTP = ""
            user.save()
            return Response({"access": str(access_token), "refresh": str(refresh_token), "user": {
                "email": user.email,
                "role": user.role,
                "user_id": user.id,
               "has_group": user.has_group,
               "photo_url": str(user.photo) if user.photo else None
            }})
        except:
            return Response(status = status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def reset_password(request, pk):
    try:
        user = User.objects.get(email = pk)
    except:
        user = None

    if user is None or user.role == "lecturer":
        return Response(status=status.HTTP_403_FORBIDDEN)

    else:
        OTP = random.getrandbits(128)

        user.OTP = OTP

        user.save()

        frontend_link = f"http://localhost:5173/reset_password/{OTP}"

        try:
            subject = 'PASSWORD RESET ON ORPMS'
            message = f'''Your account has been reset, please follow the link below to create a new password

            {frontend_link}

            Best regards,
            The ORPMS Team
            '''
            email_from = 'ORPMS TEAM'
            recipient_list = [pk]

            send_mail(subject, message, email_from, recipient_list)

            

        except:
            pass
            # return Response(status= status.HTTP_400_BAD_REQUEST

        return Response(status=status.HTTP_202_ACCEPTED)  


@api_view(['POST'])
def update_password(request, pk):

    try:
        user = User.objects.get(OTP = pk)

    except:
        user = None

    if user is None:

        return Response(status=status.HTTP_403_FORBIDDEN)

    else:
        user.password = make_password(request.data["password"])

        user.OTP = ""

        user.save()

        access_token = AccessToken.for_user(user)

        refresh_token = RefreshToken.for_user(user)

        return Response({"access": str(access_token), "refresh": str(refresh_token), "user": {
                "email": user.email,
                "role": user.role,
                "user_id": user.id,
               "has_group": user.has_group,
               "photo_url": str(user.photo) if user.photo else None
            }}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def view_all_projects(request):
    projects = Project.objects.all()
    converted = AllProjectsSerializer(projects, many = True)
    return Response(converted.data)


@api_view(['POST'])
def broadcast(request):

    try:

        groups = Group.objects.all()

        author = User.objects.get(id = request.data["author"])

        for group in groups:

            Message.objects.create(

                group = group,
                
                author = author,

                body = request.data["body"]

            )

        return Response(status=status.HTTP_201_CREATED)   

    except:

        return Response(status=status.HTTP_400_BAD_REQUEST) 
    

@api_view(['GET'])

def get_broadcasts(request, pk):

    messages = Message.objects.filter(author = pk)

    converted_messages = MessageSerializer(messages, many = True)

    return Response(converted_messages.data)