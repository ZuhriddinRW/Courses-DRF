from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
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


class UserViewSet ( viewsets.ModelViewSet ) :
    queryset = User.objects.all ()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) :
        if self.action == 'create' :
            return UserCreateSerializer
        return UserSerializer


class TeacherViewSet ( viewsets.ModelViewSet ) :
    queryset = Teacher.objects.select_related ( 'user', 'department' ).all ()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) :
        if self.action == 'create' :
            return TeacherCreateSerializer
        elif self.action in ['update', 'partial_update'] :
            return TeacherSerializer
        return TeacherDetailSerializer


class StudentViewSet ( viewsets.ModelViewSet ) :
    queryset = Student.objects.select_related ( 'user', 'course' ).all ()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) :
        if self.action == 'create' :
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update'] :
            return StudentSerializer
        return StudentDetailSerializer


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