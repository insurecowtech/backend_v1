from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(mobile_number, otp_code):
    print(f"Sending OTP {otp_code} to {mobile_number}")

# def success_response(message="", data=None, status_code=status.HTTP_200_OK):
#     return Response({
#         "statusCode": str(status_code),
#         "statusMessage": "Success",
#         "data": {
#             "message": message,
#             **(data or {} or [])
#         }
#     }, status=status_code)
from rest_framework.response import Response
from rest_framework import status

def success_response(message="", data=None, status_code=status.HTTP_200_OK):
    if isinstance(data, dict):
        response_data = {
            "message": message,
            **data
        }
    else:
        response_data = {
            "message": message,
            "results": data if data is not None else []
        }

    return Response({
        "statusCode": str(status_code),
        "statusMessage": "Success",
        "data": response_data
    }, status=status_code)


def error_response(message="", status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "statusCode": str(status_code),
        "statusMessage": "Failed",
        "data": {
            "message": message
        }
    }, status=status_code)

def handle_serializer_error(e: ValidationError):
    detail = e.detail if hasattr(e, 'detail') else str(e)

    if isinstance(detail, dict):
        message = detail.get('detail', detail)
    elif isinstance(detail, list):
        message = detail[0]
    else:
        message = str(detail)

    return error_response(str(message), status_code=status.HTTP_400_BAD_REQUEST)

def validation_error_from_serializer(serializer):
    error_messages = []

    if isinstance(serializer.errors, list):  # Bulk (many=True)
        for idx, error_dict in enumerate(serializer.errors):
            for field, errors in error_dict.items():
                if isinstance(errors, list):
                    for error in errors:
                        error_messages.append(f"Item {idx + 1} - {field}: {error}")
                else:
                    error_messages.append(f"Item {idx + 1} - {field}: {errors}")
    else:  # Single object
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            else:
                error_messages.append(f"{field}: {errors}")

    first_error_message = error_messages[0] if error_messages else "Invalid input."

    return Response({
        "statusCode": "400",
        "statusMessage": "Validation Error",
        "data": {
            "details": serializer.errors,
            "message": first_error_message
        }
    }, status=status.HTTP_400_BAD_REQUEST)
from decimal import Decimal
from datetime import date, datetime

from django.db.models.fields.files import FieldFile
from decimal import Decimal
from datetime import date, datetime

def convert_non_serializable_fields(data):
    for key, value in data.items():
        if isinstance(value, Decimal):
            data[key] = float(value)
        elif isinstance(value, date):
            data[key] = value.isoformat()  # Convert date to 'YYYY-MM-DD' string
        elif isinstance(value, datetime):
            data[key] = value.isoformat()  # Convert datetime to 'YYYY-MM-DDTHH:MM:SS' string
        elif isinstance(value, FieldFile):
            data[key] = value.url if value else None  # Get URL of the file if it exists
        elif isinstance(value, dict):
            convert_non_serializable_fields(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    convert_non_serializable_fields(item)
    return data


