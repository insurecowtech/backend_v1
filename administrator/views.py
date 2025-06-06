from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, BasePermission, IsAuthenticated, AllowAny
from rest_framework import status, permissions, serializers

from Insurecow.utils import success_response, handle_serializer_error, validation_error_from_serializer,error_response
from authservice.models import User
from authservice.serializers import UserSerializer, ChangePasswordSerializer


class IsAllowedToCreateUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.role.id == 2:
            return True
        return False

class CreateUserByAdminView(APIView):
    permission_classes = [IsAllowedToCreateUser]

    def post(self, request):
        try:
            role_id = request.user.role.id
            role_name = request.user.role.name
            print(f"Role ID: {role_id}, Role Name: {role_name}")
        except AttributeError:
            return error_response("User role not found", status_code=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                user = serializer.save()
                return success_response(
                    "User created successfully",
                    data={"user_id": user.id},
                    status_code=status.HTTP_201_CREATED
                )
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)



class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class SetManagedByView(APIView):
    permission_classes = [IsSuperUser]

    def patch(self, request, pk, *args, **kwargs):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("User's data updated successfully", data=serializer.data, status_code=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return validation_error_from_serializer(serializer)


class UserListView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        try:
            return success_response("User List Retrieved successfully", data=serializer.data,
                                    status_code=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return handle_serializer_error(e)




