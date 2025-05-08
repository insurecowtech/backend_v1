from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from .models import Breed, Color, VaccinationStatus, DewormingStatus
from .serializers import BreedSerializer, ColorSerializer, VaccinationStatusSerializer, DewormingStatusSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Asset, AssetHistory, AssetType
from .serializers import AssetSerializer, AssetTypeSerializer
from rest_framework.permissions import BasePermission
from Insurecow.utils import success_response, handle_serializer_error, validation_error_from_serializer, error_response
from administrator.views import IsSuperUser
from authservice.models import User


class AssetTypeListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assets = AssetType.objects.all()
        serializer = AssetTypeSerializer(assets, many=True)
        try:
            return success_response("Asset Type List Retrieved successfully", data=serializer.data,
                                    status_code=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return handle_serializer_error(e)
class AssetTypeCreateAPIView(APIView):
    permission_classes = [IsSuperUser]
    def post(self, request):
        serializer = AssetTypeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("Asset Type Created successfully.", data=serializer.data,status_code=status.HTTP_201_CREATED)

            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)
class AssetTypeDetailAPIView(APIView):
    permission_classes = [IsSuperUser]

    def get_object(self, pk, user):
        return get_object_or_404(AssetType, pk=pk)

    def get(self, request, pk):
        asset = self.get_object(pk, request.user)
        serializer = AssetTypeSerializer(asset)
        try:
            return success_response("Asset Details Retrieved successfully", data=serializer.data)
        except serializers.ValidationError as e:
            return handle_serializer_error(e)

    def put(self, request, pk):
        asset = self.get_object(pk, request.user)
        serializer = AssetTypeSerializer(asset, data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("Asset Type Updated successfully", data=serializer.data)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)
        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        asset = self.get_object(pk, request.user)
        asset.delete()
        return success_response("Deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)

class IsAllowedToCreateAsset(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if hasattr(request.user, 'role') and request.user.role == 2:
            return True
        return False


# class AssetCreateOnBehalfAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsAllowedToCreateAsset]
#
#     def post(self, request):
#         user_id = request.data.get('user_id')  # Get the user ID from the request
#         if not user_id:
#             return Response({"detail": "User ID must be provided."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#
#
#         serializer = AssetSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             try:
#                 asset = serializer.save(owner=user, created_by=request.user, updated_by=request.user)
#                 AssetHistory.objects.create(
#                     asset=asset,
#                     changed_by=request.user,
#                     weight_kg=asset.weight_kg,
#                     vaccination_status=asset.vaccination_status,
#                     deworming_status=asset.deworming_status,
#                     remarks="Initial asset creation on behalf of user"
#                 )
#
#                 return success_response("Asset Created successfully.",
#                                         data=AssetSerializer(asset).data,
#                                         status_code=status.HTTP_201_CREATED)
#             except serializers.ValidationError as e:
#                 return handle_serializer_error(e)
#
#         return validation_error_from_serializer(serializer)



class BreedListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        breeds = Breed.objects.all()
        serializer = BreedSerializer(breeds, many=True)
        return success_response("Breed List Retrieved successfully", data=serializer.data, status_code=status.HTTP_200_OK)
class BreedCreateAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = BreedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Breed Created successfully", data=serializer.data, status_code=status.HTTP_201_CREATED)
        return validation_error_from_serializer(serializer)
class BreedDetailAPIView(APIView):
    permission_classes = [IsSuperUser]

    def get_object(self, pk):
        return get_object_or_404(Breed, pk=pk)

    def get(self, request, pk):
        breed = self.get_object(pk)
        serializer = BreedSerializer(breed)
        return success_response("Breed Retrieved successfully", data=serializer.data, status_code=status.HTTP_200_OK)

    def put(self, request, pk):
        breed = self.get_object(pk)
        serializer = BreedSerializer(breed, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Breed Updated successfully", data=serializer.data,
                                    status_code=status.HTTP_200_OK)

        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        breed = self.get_object(pk)
        breed.delete()
        return success_response("Breed Deleted successfully", status_code=status.HTTP_204_NO_CONTENT)


class ColorListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        colors = Color.objects.all()
        serializer = ColorSerializer(colors, many=True)
        return success_response("Color List Retrieved  successfully", data=serializer.data,
                                status_code=status.HTTP_200_OK)
class ColorCreateAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = ColorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Color Created  successfully", data=serializer.data,
                                    status_code=status.HTTP_201_CREATED)
        return validation_error_from_serializer(serializer)
class ColorDetailAPIView(APIView):
    permission_classes = [IsSuperUser]

    def get_object(self, pk):
        return get_object_or_404(Color, pk=pk)

    def get(self, request, pk):
        color = self.get_object(pk)
        serializer = ColorSerializer(color)
        return success_response("Color Retrieved  successfully", data=serializer.data,
                                status_code=status.HTTP_200_OK)
    def put(self, request, pk):
        color = self.get_object(pk)
        serializer = ColorSerializer(color, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Color Updated  successfully", data=serializer.data,
                                    status_code=status.HTTP_200_OK)
        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        color = self.get_object(pk)
        color.delete()
        return success_response("Color Deleted  successfully",status_code=status.HTTP_204_NO_CONTENT)


class VaccinationStatusListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        statuses = VaccinationStatus.objects.all()
        serializer = VaccinationStatusSerializer(statuses, many=True)
        return success_response("Vaccination Status List Retrieved successfully", data=serializer.data,
                                status_code=status.HTTP_200_OK)
class VaccinationStatusCreateAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = VaccinationStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Vaccination Status Created successfully", data=serializer.data,
                                    status_code=status.HTTP_201_CREATED)
        return validation_error_from_serializer(serializer)
class VaccinationStatusDetailAPIView(APIView):
    permission_classes = [IsSuperUser]

    def get_object(self, pk):
        return get_object_or_404(VaccinationStatus, pk=pk)

    def get(self, request, pk):
        statuss = self.get_object(pk)
        serializer = VaccinationStatusSerializer(statuss)
        return success_response("Vaccination Status  Retrieved successfully", data=serializer.data, status_code=status.HTTP_200_OK)
    def put(self, request, pk):
        statuss = self.get_object(pk)
        serializer = VaccinationStatusSerializer(statuss, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Vaccination Status Updated successfully", data=serializer.data,
                                    status_code=status.HTTP_200_OK)

        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        statuss = self.get_object(pk)
        statuss.delete()
        return success_response("Vaccination Status Deleted successfully", status_code=status.HTTP_204_NO_CONTENT)

class DewormingStatusListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        statuses = DewormingStatus.objects.all()
        serializer = DewormingStatusSerializer(statuses, many=True)
        return success_response("Deworming Status List Retrieved successfully", data=serializer.data,
                                status_code=status.HTTP_200_OK)
class DewormingStatusCreateAPIView(APIView):
    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = DewormingStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Deworming Status Created successfully", data=serializer.data,
                                    status_code=status.HTTP_201_CREATED)
        return validation_error_from_serializer(serializer)
class DewormingStatusDetailAPIView(APIView):
    permission_classes = [IsSuperUser]

    def get_object(self, pk):
        return get_object_or_404(DewormingStatus, pk=pk)

    def get(self, request, pk):
        statuss = self.get_object(pk)
        serializer = DewormingStatusSerializer(statuss)
        return success_response("Deworming Status Retrieved successfully", data=serializer.data,
                                status_code=status.HTTP_200_OK)
    def put(self, request, pk):
        statuss = self.get_object(pk)
        serializer = DewormingStatusSerializer(statuss, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Deworming Status Updated successfully", data=serializer.data,
                                    status_code=status.HTTP_200_OK)
        return validation_error_from_serializer(serializer)

    def delete(self, request, pk):
        statuss = self.get_object(pk)
        statuss.delete()
        return success_response("Deworming Status Deleted successfully",status_code=status.HTTP_204_NO_CONTENT)



class AssetListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            assets = Asset.objects.all()
        else:
            assets = Asset.objects.filter(owner=request.user)

        serializer = AssetSerializer(assets, many=True)
        try:
            return success_response(
                "Asset List Retrieved successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except serializers.ValidationError as e:
            return handle_serializer_error(e)

class AssetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AssetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return success_response("Asset Created successfully.", data=serializer.data, status_code=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return handle_serializer_error(e)

        return validation_error_from_serializer(serializer)

class AssetDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Asset, pk=pk)

    def get(self, request, pk):
        try:
            if request.user.is_superuser:
                asset = self.get_object(pk)
            else:
                asset = Asset.objects.get(pk=pk, owner=request.user)

            serializer = AssetSerializer(asset)
            return success_response("Asset Details Retrieved successfully", data=serializer.data)

        except Asset.DoesNotExist:
            return error_response("Asset not found.", status_code=status.HTTP_404_NOT_FOUND)

        except AttributeError as e:
            return error_response(f"Attribute error: {str(e)}", status_code=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            return handle_serializer_error(e)

    def put(self, request, pk):
        try:
            if request.user.is_superuser:
                asset = self.get_object(pk)
            else:
                asset = Asset.objects.get(pk=pk, owner=request.user)
            serializer = AssetSerializer(asset, data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return success_response("Asset Updated successfully", data=serializer.data)
                except serializers.ValidationError as e:
                    return handle_serializer_error(e)
            return validation_error_from_serializer(serializer)
        except Asset.DoesNotExist:
            return error_response("Asset not found.", status_code=status.HTTP_404_NOT_FOUND)

        except AttributeError as e:
            return error_response(f"Attribute error: {str(e)}", status_code=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            return handle_serializer_error(e)

    def delete(self, request, pk):
        try:
            if request.user.is_superuser:
                asset = self.get_object(pk)
            else:
                asset = Asset.objects.get(pk=pk, owner=request.user)
            asset.delete()
            return success_response("Asset Deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)
        except Asset.DoesNotExist:
            return error_response("Asset not found.", status_code=status.HTTP_404_NOT_FOUND)

        except AttributeError as e:
            return error_response(f"Attribute error: {str(e)}", status_code=status.HTTP_404_NOT_FOUND)

        except serializers.ValidationError as e:
            return handle_serializer_error(e)