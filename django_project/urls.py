from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django_app.views import *

schema_view = get_schema_view (
    openapi.Info (
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact ( email="contact@snippets.local" ),
        license=openapi.License ( name="BSD License" ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter ()
router.register ( r'users', UserViewSet, basename='user' )
router.register ( r'teachers', TeacherViewSet, basename='teacher' )
router.register ( r'students', StudentViewSet, basename='student' )
router.register ( r'courses', CourseViewSet, basename='course' )
router.register ( r'departments', DepartmentViewSet, basename='department' )
router.register ( r'day', DayViewSet, basename='day' )
router.register ( r'rooms', RoomsViewSet, basename='rooms' )
router.register ( r'table', TableViewSet, basename='table' )
router.register ( r'table_type', TableTypeViewSet, basename='table_type' )
router.register ( r'group_student', GroupStudentViewSet, basename='group_student' )

urlpatterns = [
    path ( 'admin/', admin.site.urls ),
    path ( '', include ( router.urls ) ),

    path ( 'api/token/', LoginUser.as_view (), name='token_obtain_pair' ),
    path ( 'api/token/refresh/', TokenRefreshView.as_view (), name='token_refresh' ),
    path ( 'api/token/verify/', TokenVerifyView.as_view (), name='token_verify' ),

    path ( 'swagger<format>/', schema_view.without_ui ( cache_timeout=0 ), name='schema-json' ),
    path ( 'swagger/', schema_view.with_ui ( 'swagger', cache_timeout=0 ), name='schema-swagger-ui' ),
    path ( 'redoc/', schema_view.with_ui ( 'redoc', cache_timeout=0 ), name='schema-redoc' ),
]
