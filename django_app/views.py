from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_app.make_token import get_tokens_for_user
from django_app.serializers import (
    LoginSerializer, UserSerializer, UserCreateSerializer,
    TeacherSerializer, TeacherCreateSerializer, TeacherDetailSerializer,
    StudentSerializer, StudentCreateSerializer, StudentDetailSerializer,
    CourseSerializer, DepartmentSerializer
)
from django_app.models import User, Teacher, Student, Course, Departments


# ==================== Authentication ====================

class LoginUser(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        token = get_tokens_for_user(user)
        return Response(data=token, status=status.HTTP_200_OK)


# ==================== User ViewSet ====================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


# ==================== Teacher ViewSet ====================

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'department').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeacherSerializer
        return TeacherDetailSerializer


# ==================== Student ViewSet ====================

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'course').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentSerializer
        return StudentDetailSerializer


# ==================== Course ViewSet ====================

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


# ==================== Department ViewSet ====================

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]