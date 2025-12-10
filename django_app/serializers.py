from django.contrib.auth import authenticate
from rest_framework import serializers
from django_app.models import User, Teacher, Student, Course, Departments


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
                  'is_active', 'is_staff', 'is_admin', 'is_teacher', 'is_student']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number',
                  'password', 'password_confirm', 'is_teacher', 'is_student']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)

            if not user:
                raise serializers.ValidationError(
                    'Phone number or password is invalid'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled'
                )

            data['user'] = user
            return data
        else:
            raise serializers.ValidationError(
                'Must include "phone number" and "password"'
            )


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ['id', 'title', 'is_active', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    department_name = serializers.CharField(source='department.title', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'user_id', 'department', 'department_name',
                  'bio', 'specialization', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_user_id(self, value):
        if hasattr(value, 'teacher_profile'):
            raise serializers.ValidationError("This user already has a teacher profile")
        return value


class TeacherCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = Teacher
        fields = ['user', 'department', 'bio', 'specialization']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_teacher'] = True
        user = UserCreateSerializer().create(user_data)
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    course_name = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'user_id', 'course', 'course_name',
                  'student_id', 'enrollment_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_user_id(self, value):
        if hasattr(value, 'student_profile'):
            raise serializers.ValidationError("This user already has a student profile")
        return value


class StudentCreateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = Student
        fields = ['user', 'course', 'student_id', 'enrollment_date']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['is_student'] = True
        user = UserCreateSerializer().create(user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student


class TeacherDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'department', 'bio', 'specialization', 'created_at', 'updated_at']


class StudentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    course = CourseSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'course', 'student_id', 'enrollment_date', 'created_at', 'updated_at']