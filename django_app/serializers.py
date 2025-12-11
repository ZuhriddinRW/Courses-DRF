from django.contrib.auth import authenticate
from rest_framework import serializers
from django_app.models import *


class UserSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
                  'is_active', 'is_staff', 'is_admin', 'is_teacher', 'is_student']
        read_only_fields = ['id']


class UserCreateSerializer ( serializers.ModelSerializer ) :
    password = serializers.CharField ( write_only=True, required=True, style={'input_type' : 'password'} )
    password_confirm = serializers.CharField ( write_only=True, required=True, style={'input_type' : 'password'} )

    class Meta :
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number',
                  'password', 'password_confirm', 'is_teacher', 'is_student']

    def validate_email(self, value) :
        if not value :
            raise serializers.ValidationError ( "Email is required" )
        if User.objects.filter ( email=value ).exists () :
            raise serializers.ValidationError ( "Email already exists" )
        return value

    def validate(self, data) :
        if data['password'] != data['password_confirm'] :
            raise serializers.ValidationError ( "Passwords do not match" )
        return data

    def create(self, validated_data) :
        validated_data.pop ( 'password_confirm' )
        password = validated_data.pop ( 'password' )
        user = User.objects.create_user ( **validated_data )
        user.set_password ( password )
        user.save ()
        return user


class LoginSerializer ( serializers.Serializer ) :
    email = serializers.EmailField ()
    password = serializers.CharField ( write_only=True )

    def validate(self, data) :
        email = data.get ( 'email' )
        password = data.get ( 'password' )

        if email and password :
            try :
                user = User.objects.get ( email=email )
                if not user.check_password ( password ) :
                    raise serializers.ValidationError (
                        'Email or password is invalid'
                    )
            except User.DoesNotExist :
                raise serializers.ValidationError (
                    'Email or password is invalid'
                )

            if not user.is_active :
                raise serializers.ValidationError (
                    'Your account is not active. Please change your password to activate your account.'
                )

            data['user'] = user
            return data
        else :
            raise serializers.ValidationError (
                'Must include "email" and "password"'
            )


class ChangePasswordSerializer ( serializers.Serializer ) :
    old_password = serializers.CharField ( write_only=True, required=True )
    new_password = serializers.CharField ( write_only=True, required=True )
    new_password_confirm = serializers.CharField ( write_only=True, required=True )

    def validate_old_password(self, value) :
        user = self.context['request'].user
        if not user.check_password ( value ) :
            raise serializers.ValidationError ( "Old password is incorrect" )
        return value

    def validate(self, data) :
        if data['new_password'] != data['new_password_confirm'] :
            raise serializers.ValidationError ( "New passwords do not match" )

        if data['old_password'] == data['new_password'] :
            raise serializers.ValidationError ( "New password must be different from old password" )

        return data


class ActivateAccountSerializer ( serializers.Serializer ) :
    email = serializers.EmailField ( required=True )
    current_password = serializers.CharField ( write_only=True, required=True )
    new_password = serializers.CharField ( write_only=True, required=True )
    new_password_confirm = serializers.CharField ( write_only=True, required=True )

    def validate_email(self, value) :
        try :
            user = User.objects.get ( email=value )
            if user.is_active :
                raise serializers.ValidationError (
                    "This account is already active. Please use the login page."
                )
        except User.DoesNotExist :
            raise serializers.ValidationError ( "No account found with this email" )
        return value

    def validate(self, data) :
        try :
            user = User.objects.get ( email=data['email'] )
        except User.DoesNotExist :
            raise serializers.ValidationError ( "Invalid credentials" )

        if not user.check_password ( data['current_password'] ) :
            raise serializers.ValidationError (
                "Current password is incorrect"
            )

        if data['new_password'] != data['new_password_confirm'] :
            raise serializers.ValidationError ( "New passwords do not match" )

        if data['current_password'] == data['new_password'] :
            raise serializers.ValidationError (
                "New password must be different from current password"
            )

        data['user'] = user
        return data


class DepartmentSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = Departments
        fields = ['id', 'title', 'is_active', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = Course
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherSerializer ( serializers.ModelSerializer ) :
    user = UserSerializer ( read_only=True )
    user_id = serializers.PrimaryKeyRelatedField (
        queryset=User.objects.all (),
        source='user',
        write_only=True
    )
    department_name = serializers.CharField ( source='department.title', read_only=True )

    class Meta :
        model = Teacher
        fields = ['id', 'user', 'user_id', 'department', 'department_name',
                  'bio', 'specialization', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_user_id(self, value) :
        if hasattr ( value, 'teacher_profile' ) :
            raise serializers.ValidationError ( "This user already has a teacher profile" )
        return value


class TeacherCreateSerializer ( serializers.ModelSerializer ) :
    user = UserCreateSerializer ()

    class Meta :
        model = Teacher
        fields = ['user', 'department', 'bio', 'specialization']

    def create(self, validated_data) :
        user_data = validated_data.pop ( 'user' )
        user_data['is_teacher'] = True
        user = UserCreateSerializer ().create ( user_data )
        teacher = Teacher.objects.create ( user=user, **validated_data )
        return teacher


class StudentSerializer ( serializers.ModelSerializer ) :
    user = UserSerializer ( read_only=True )
    user_id = serializers.PrimaryKeyRelatedField (
        queryset=User.objects.all (),
        source='user',
        write_only=True
    )
    course_name = serializers.CharField ( source='course.title', read_only=True )

    class Meta :
        model = Student
        fields = ['id', 'user', 'user_id', 'course', 'course_name',
                  'student_id', 'enrollment_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_user_id(self, value) :
        if hasattr ( value, 'student_profile' ) :
            raise serializers.ValidationError ( "This user already has a student profile" )
        return value


class StudentCreateSerializer ( serializers.ModelSerializer ) :
    user = UserCreateSerializer ()

    class Meta :
        model = Student
        fields = ['user', 'email', 'course', 'student_id', 'enrollment_date']

    def create(self, validated_data) :
        user_data = validated_data.pop ( 'user' )
        user_data['is_student'] = True
        user = UserCreateSerializer ().create ( user_data )
        student = Student.objects.create ( user=user, **validated_data )
        return student


class TeacherDetailSerializer ( serializers.ModelSerializer ) :
    user = UserSerializer ()
    department = DepartmentSerializer ()

    class Meta :
        model = Teacher
        fields = ['id', 'user', 'department', 'bio', 'specialization', 'created_at', 'updated_at']


class StudentDetailSerializer ( serializers.ModelSerializer ) :
    user = UserSerializer ()
    course = CourseSerializer ()

    class Meta :
        model = Student
        fields = ['id', 'user', 'course', 'student_id', 'enrollment_date', 'created_at', 'updated_at']


class GroupStudentSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = GroupStudent
        fields = '__all__'


class TableSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = Table
        fields = '__all__'


class TableTypeSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = TableType
        fields = '__all__'


class RoomsSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = Rooms
        fields = '__all__'


class DaySerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = Day
        fields = '__all__'


class SendEmail ( serializers.Serializer ) :
    text = serializers.CharField ()
    email = serializers.EmailField ()