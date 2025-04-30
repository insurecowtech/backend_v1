# views.py
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
import jwt
from django.conf import settings

from administrator.views import IsSuperUser
from .models import UserNomineeInfo, UserFinancialInfo, UserPersonalInfo
from .serializers import Step1Serializer, OTPVerifySerializer, SetPasswordSerializer, LoginSerializer, \
    SetPersonalInfoSerializer, SetFinancialInfoSerializer, SetNomineeInfoSerializer, SetOrganizationInfoSerializer
from Insurecow.utils import handle_serializer_error, success_response, validation_error_from_serializer, error_response

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Role
from .serializers import RoleSerializer
from rest_framework.permissions import IsAuthenticated  # Optional: Add authentication if needed


class RoleListCreateAPIView(APIView):
    permission_classes = [AllowAny]  # Optional: Add permission classes as needed

    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        try:
            return success_response("Roles Retrieved successfully.", data=serializer.data)

        except serializers.ValidationError as e:
            return handle_serializer_error(e)


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
    permission_classes = [IsSuperUser]  # Optional: Add permission classes as needed

    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return None

    def get(self, request, pk):
        role = self.get_object(pk)
        if role is not None:
            serializer = RoleSerializer(role)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return success_response("Roles Retrieved successfully.", data=serializer.data, status_code=status.HTTP_201_CREATED)

                except serializers.ValidationError as e:
                    return handle_serializer_error(e)

            return validation_error_from_serializer(serializer)
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

class SetFinancialInfo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SetFinancialInfoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("User's Personal Info Saved Successfully.")
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
                return success_response("User's Personal Info Saved Successfully.")
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
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

