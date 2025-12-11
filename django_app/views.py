from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_app.make_token import get_tokens_for_user
from django_app.serializers import *
from django_app.models import User, Teacher, Student, Course, Departments


class LoginUser ( APIView ) :
    permission_classes = [AllowAny]

    @swagger_auto_schema ( request_body=LoginSerializer )
    def post(self, request) :
        serializer = LoginSerializer ( data=request.data )
        serializer.is_valid ( raise_exception=True )
        user = serializer.validated_data.get ( "user" )
        token = get_tokens_for_user ( user )
        return Response ( data=token, status=status.HTTP_200_OK )


class ChangePasswordView ( APIView ) :
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema ( request_body=ChangePasswordSerializer )
    def post(self, request) :
        serializer = ChangePasswordSerializer ( data=request.data, context={'request' : request} )
        serializer.is_valid ( raise_exception=True )

        user = request.user
        user.set_password ( serializer.validated_data['new_password'] )
        user.save ()

        return Response (
            {"message" : "Password changed successfully."},
            status=status.HTTP_200_OK
        )


class ActivateAccountView ( APIView ) :
    permission_classes = [AllowAny]

    @swagger_auto_schema ( request_body=ActivateAccountSerializer )
    def post(self, request) :
        serializer = ActivateAccountSerializer ( data=request.data )
        serializer.is_valid ( raise_exception=True )

        user = serializer.validated_data['user']
        user.set_password ( serializer.validated_data['new_password'] )
        user.is_active = True
        user.save ()

        token = get_tokens_for_user ( user )

        return Response (
            {
                "message" : "Account activated successfully. You can now login.",
                "token" : token
            },
            status=status.HTTP_200_OK
        )


class UserViewSet ( viewsets.ModelViewSet ) :
    queryset = User.objects.all ()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self) :
        if self.action == 'create' :
            return UserCreateSerializer
        return UserSerializer


class TeacherViewSet ( viewsets.ModelViewSet ) :
    queryset = Teacher.objects.select_related ( 'user', 'department' ).all ()
    permission_classes = [IsAuthenticated]

    def get_permissions(self) :
        if self.action in ['create', 'update', 'partial_update', 'destroy'] :
            return [IsAuthenticated (), IsAdminUser ()]
        return [IsAuthenticated ()]

    def get_serializer_class(self) :
        if self.action == 'create' :
            return TeacherCreateSerializer
        elif self.action in ['update', 'partial_update'] :
            return TeacherSerializer
        return TeacherDetailSerializer


class StudentViewSet ( viewsets.ModelViewSet ) :
    queryset = Student.objects.select_related ( 'user', 'course' ).all ()
    permission_classes = [IsAuthenticated]

    def get_permissions(self) :
        if self.action in ['create', 'update', 'partial_update', 'destroy'] :
            return [IsAuthenticated (), IsAdminUser ()]
        return [IsAuthenticated ()]

    def get_serializer_class(self) :
        if self.action == 'create' :
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update'] :
            return StudentSerializer
        return StudentDetailSerializer

    def create(self, request, *args, **kwargs) :
        default_password = "DefaultPass123!"

        serializer = self.get_serializer ( data=request.data )
        serializer.is_valid ( raise_exception=True )
        student = serializer.save ()

        user = student.user

        # is_active=False qilish
        user.is_active = False
        user.set_password ( default_password )
        user.save ()

        try :
            subject = "Your Student Account Credentials"
            message = f"""
Hello {user.first_name or 'Student'},

Your student account has been created successfully.

Login credentials:
Email: {user.email}
Password: {default_password}

IMPORTANT: Please activate your account using the following steps:
1. Go to the activation page
2. Enter your email: {user.email}
3. Enter the temporary password: {default_password}
4. Set your new password

Your account will be activated after you set a new password.

Best regards,
Admin Team
            """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail ( subject, message, email_from, recipient_list )
        except Exception as e :
            print ( f"Email sending error: {e}" )

        headers = self.get_success_headers ( serializer.data )
        return Response (
            {
                **serializer.data,
                "message" : "Student created. Email sent with activation instructions."
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CourseViewSet ( viewsets.ModelViewSet ) :
    queryset = Course.objects.all ()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class DepartmentViewSet ( viewsets.ModelViewSet ) :
    queryset = Departments.objects.all ()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class DayViewSet ( viewsets.ModelViewSet ) :
    queryset = Day.objects.all ()
    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated]


class TableViewSet ( viewsets.ModelViewSet ) :
    queryset = Table.objects.all ()
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]


class TableTypeViewSet ( viewsets.ModelViewSet ) :
    queryset = TableType.objects.all ()
    serializer_class = TableTypeSerializer
    permission_classes = [IsAuthenticated]


class RoomsViewSet ( viewsets.ModelViewSet ) :
    queryset = Rooms.objects.all ()
    serializer_class = RoomsSerializer
    permission_classes = [IsAuthenticated]


class GroupStudentViewSet ( viewsets.ModelViewSet ) :
    queryset = GroupStudent.objects.all ()
    serializer_class = GroupStudentSerializer
    permission_classes = [IsAuthenticated]