from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from authservice.models import User
from .models import Asset, AssetHistory
from .serializers import AssetSerializer


class AssetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            asset = serializer.save()

            # Create initial asset history
            AssetHistory.objects.create(
                asset=asset,
                changed_by=request.user,
                weight_kg=asset.weight_kg,
                vaccination_status=asset.vaccination_status,
                deworming_status=asset.deworming_status,
                remarks="Initial asset creation"
            )

            return Response(AssetSerializer(asset, context={'request': request}).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AssetListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assets = Asset.objects.filter(owner=request.user)
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Asset, pk=pk, owner=user)

    def get(self, request, pk):
        asset = self.get_object(pk, request.user)
        serializer = AssetSerializer(asset)
        return Response(serializer.data)

    def put(self, request, pk):
        asset = self.get_object(pk, request.user)
        serializer = AssetSerializer(asset, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        asset = self.get_object(pk, request.user)
        asset.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Asset, AssetHistory
from .serializers import AssetSerializer
from rest_framework.permissions import BasePermission


class IsAllowedToCreateAsset(BasePermission):
    """
    Custom permission to allow asset creation only for staff, superuser, or users with role 2.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and has the correct role
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

        # Ensure the user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the user is allowed to create assets on their behalf
        # Here we can add additional checks if necessary, e.g., user roles, etc.

        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Manually set the owner to the specified user
            asset = serializer.save(owner=user, created_by=request.user, updated_by=request.user)

            # Manually create initial asset history
            AssetHistory.objects.create(
                asset=asset,
                changed_by=request.user,
                weight_kg=asset.weight_kg,
                vaccination_status=asset.vaccination_status,
                deworming_status=asset.deworming_status,
                remarks="Initial asset creation on behalf of user"
            )

            return Response(AssetSerializer(asset).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
