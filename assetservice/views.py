from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from Insurecow.utils import success_response, handle_serializer_error, validation_error_from_serializer
from authservice.models import User


class AssetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                asset = serializer.save()
                AssetHistory.objects.create(
                    asset=asset,
                    changed_by=request.user,
                    weight_kg=asset.weight_kg,
                    vaccination_status=asset.vaccination_status,
                    deworming_status=asset.deworming_status,
                    remarks="Initial asset creation"
                )

                return success_response("Asset Created successfully.",
                                        data=AssetSerializer(asset, context={'request': request}).data,
                                        status_code=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)


class AssetListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assets = Asset.objects.filter(owner=request.user)
        serializer = AssetSerializer(assets, many=True)
        if serializer.is_valid():
            try:
                return success_response("Asset List Retrieved successfully", data=serializer.data,
                                        status_code=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return validation_error_from_serializer(serializer)


class AssetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Asset, pk=pk, owner=user)

    def get(self, request, pk):
        asset = self.get_object(pk, request.user)
        serializer = AssetSerializer(asset)
        if serializer.is_valid():
            try:
                return success_response("Asset Details Retrieved successfully", data=serializer.data)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return validation_error_from_serializer(serializer)

    def put(self, request, pk):
        asset = self.get_object(pk, request.user)
        serializer = AssetSerializer(asset, data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("Asset Details Updated successfully", data=serializer.data)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        asset = self.get_object(pk, request.user)
        asset.delete()
        return success_response("Deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Asset, AssetHistory
from .serializers import AssetSerializer
from rest_framework.permissions import BasePermission


class IsAllowedToCreateAsset(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if hasattr(request.user, 'role') and request.user.role == 2:
            return True
        return False


class AssetCreateOnBehalfAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAllowedToCreateAsset]

    def post(self, request):
        user_id = request.data.get('user_id')  # Get the user ID from the request
        if not user_id:
            return Response({"detail": "User ID must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                asset = serializer.save(owner=user, created_by=request.user, updated_by=request.user)
                AssetHistory.objects.create(
                    asset=asset,
                    changed_by=request.user,
                    weight_kg=asset.weight_kg,
                    vaccination_status=asset.vaccination_status,
                    deworming_status=asset.deworming_status,
                    remarks="Initial asset creation on behalf of user"
                )

                return success_response("Asset Created successfully.",
                                        data=AssetSerializer(asset).data,
                                        status_code=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)
