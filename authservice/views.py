# views.py
from pyexpat.errors import messages
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
import jwt
from django.conf import settings

from administrator.views import IsSuperUser
from .models import UserNomineeInfo, UserFinancialInfo, UserPersonalInfo, OrganizationInfo
from .serializers import Step1Serializer, OTPVerifySerializer, SetPasswordSerializer, LoginSerializer, \
    SetPersonalInfoSerializer, SetFinancialInfoSerializer, SetNomineeInfoSerializer, SetOrganizationInfoSerializer, \
    SubUserSerializer, ChangePasswordSerializer
from Insurecow.utils import handle_serializer_error, success_response, validation_error_from_serializer, error_response

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Role
from .serializers import RoleSerializer
from rest_framework.permissions import IsAuthenticated

class RoleListAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        try:
            return success_response("Roles Retrieved successfully.", data=serializer.data)

        except serializers.ValidationError as e:
            return handle_serializer_error(e)

class RoleListCreateAPIView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("Roles Created successfully.", data=serializer.data,status_code=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)



class RoleRetrieveUpdateDestroyAPIView(APIView):
    permission_classes = [IsSuperUser]

    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return None

    def get(self, request, pk):
        role = self.get_object(pk)
        if role is not None:
            serializer = RoleSerializer(role)
            try:
                return success_response("Roles Retrieved successfully.", data=serializer.data, status_code=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return error_response("Role not found", status_code=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        role = self.get_object(pk)
        if role is not None:
            serializer = RoleSerializer(role, data=request.data)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return success_response("Roles Updated successfully.", data=serializer.data,
                                            status_code=status.HTTP_201_CREATED)

                except serializers.ValidationError as e:
                    return handle_serializer_error(e)

            return validation_error_from_serializer(serializer)
        return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        role = self.get_object(pk)
        if role is not None:
            role.delete()
            return success_response("Roles Updated successfully.",
                                status_code=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)



class RegisterStep1(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = Step1Serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("OTP sent successfully.")

            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)


class VerifyOTP(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("OTP verified successfully.")
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)


class SetPassword(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("User registered successfully.")
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)


class Login(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(
                "User logged in successfully.",
                data=serializer.validated_data
            )

        return validation_error_from_serializer(serializer)

class SetPersonalInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetPersonalInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("User's Personal Info Saved Successfully.")
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)

    def get(self, request):
        try:
            personal_info = UserPersonalInfo.objects.get(user=request.user)
            serializer = SetPersonalInfoSerializer(personal_info)
            return success_response(data=serializer.data)
        except UserNomineeInfo.DoesNotExist:
            return Response({
                "statusCode": "404",
                "statusMessage": "Not Found",
                "data": {
                    "message": "Personal info not found for this user."
                }
            }, status=status.HTTP_404_NOT_FOUND)

class SetOrganizationInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role.id == 1:
            messages = 'Organization info is not needed for this user.'
            return Response({
                "statusCode": "404",
                "statusMessage": "Not Found",
                "data": {
                    "message": f'{messages}'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SetOrganizationInfoSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return success_response("User's Organization Info Saved Successfully.")
                except serializers.ValidationError as e:
                    return handle_serializer_error(e)

            return validation_error_from_serializer(serializer)

    def get(self, request):
        try:
            organization_info = OrganizationInfo.objects.get(user=request.user)
            serializer = SetOrganizationInfoSerializer(organization_info)
            return success_response(data=serializer.data)
        except OrganizationInfo.DoesNotExist:
            messages = 'Organization info not found for this user.'
            if request.user.role.id == 1:
                messages = 'Organization info is not needed for this user.'
            return Response({
                "statusCode": "404",
                "statusMessage": "Not Found",
                "data": {
                    "message": f'{messages}'
                }
            }, status=status.HTTP_404_NOT_FOUND)

class SetFinancialInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetFinancialInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("User's Financial Info Saved Successfully.")
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return validation_error_from_serializer(serializer)

    def get(self, request):
        try:
            financial_info = UserFinancialInfo.objects.get(user=request.user)
            serializer = SetFinancialInfoSerializer(financial_info)
            return success_response(data=serializer.data)
        except UserNomineeInfo.DoesNotExist:
            return Response({
                "statusCode": "404",
                "statusMessage": "Not Found",
                "data": {
                    "message": "Financial info not found for this user."
                }
            }, status=status.HTTP_404_NOT_FOUND)

class SetNomineeInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetNomineeInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("User's Nominee Info Saved Successfully.")
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
            except Exception as e:
                return Response({
                    "statusCode": "500",
                    "statusMessage": "Internal Server Error",
                    "data": {
                        "message": str(e)
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return validation_error_from_serializer(serializer)

    def get(self, request):
        try:
            nominee_info = UserNomineeInfo.objects.get(user=request.user)
            serializer = SetNomineeInfoSerializer(nominee_info)
            return success_response(data=serializer.data)
        except UserNomineeInfo.DoesNotExist:
            return Response({
                "statusCode": "404",
                "statusMessage": "Not Found",
                "data": {
                    "message": "Nominee info not found for this user."
                }
            }, status=status.HTTP_404_NOT_FOUND)
class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"detail": "Token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            return Response(payload, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Token expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

class SubUsersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user

        # Avoid AttributeError if role is None
        if current_user.is_superuser and current_user.role is None:
            return error_response(
                {"detail": "You are a superuser. Use the dedicated API to get all users."},
                status_code=status.HTTP_403_FORBIDDEN
            )

        if not current_user.role or current_user.role.id != 2:
            return error_response(
                {"detail": "You are not authorized to view sub-users."},
                status_code=status.HTTP_403_FORBIDDEN
            )

        sub_users = current_user.sub_users.all()
        serializer = SubUserSerializer(sub_users, many=True)
        return success_response("User List retrieved successfully.", data=serializer.data)

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can change their password.

    def post(self, request):
        # Get the serializer with request data
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        # Validate the serializer data
        if serializer.is_valid():
            user = request.user  # Get the currently logged-in user

            # Set the new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()  # Save the user with the updated password

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
