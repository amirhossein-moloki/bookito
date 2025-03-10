import requests
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from customers.models import Customer
from .models import Address
from .serializers import AddressSerializer


YOUR_API_KEY = 'API_KEY'

class AddressViewSet(viewsets.ModelViewSet):
    """
    این ViewSet فقط آدرس‌های مرتبط با Customer فعلی را نمایش و مدیریت می‌کند.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        فقط آدرس‌های متعلق به Customer مرتبط با کاربر درخواست‌دهنده را برمی‌گرداند.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        return Address.objects.filter(customer=customer)

    def perform_create(self, serializer):
        """
        هنگام ایجاد آدرس، `Customer` را از `User` درخواست‌دهنده دریافت کرده و به آدرس اضافه می‌کند.
        """
        # دریافت داده‌ها از مدل Customer
        customer = get_object_or_404(Customer, user=self.request.user)
        address_data = {
            "cellPhoneNo": customer.phone_number,  # استفاده از phone_number از Customer
            "firstName": customer.first_name,  # استفاده از first_name از Customer
            "lastName": customer.last_name,  # استفاده از last_name از Customer
            "nationalId": customer.national_id,  # استفاده از national_id از Customer
            "addressStatus": 1,  # وضعیت آدرس (مثلاً منزل)
            "postcode": self.request.data.get("postal_code"),
            "selfReportingAddress": self.request.data.get("street_address"),
            "buildingNumber": self.request.data.get("house_number"),
            "floor": self.request.data.get("floor"),
            "unit": self.request.data.get("unit_number")
        }

        # ارسال درخواست به API پستکس برای احراز آدرس
        response = requests.post(
            "https://api.postex.ir/api/v1/address-verify",
            json=address_data,
            headers={"Authorization": f"ApiKey {YOUR_API_KEY}"}
        )

        if response.status_code == 200:
            # آدرس تایید شد
            serializer.save(customer=customer)
            return Response(
                {"message": "آدرس جدید با موفقیت ایجاد شد."},
                status=status.HTTP_201_CREATED
            )
        else:
            # اگر آدرس تایید نشد
            return Response(
                {"error": "آدرس وارد شده معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        حذف آدرس فقط در صورتی امکان‌پذیر است که متعلق به `Customer` درخواست‌دهنده باشد.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        address = get_object_or_404(Address, id=kwargs["pk"], customer=customer)
        address.delete()
        return Response(
            {"message": "آدرس با موفقیت حذف شد."},
            status=status.HTTP_204_NO_CONTENT
        )

    def update(self, request, *args, **kwargs):
        """
        ویرایش آدرس فقط در صورتی امکان‌پذیر است که متعلق به `Customer` درخواست‌دهنده باشد.
        """
        # دریافت داده‌ها از مدل Customer
        customer = get_object_or_404(Customer, user=request.user)
        address_data = {
            "cellPhoneNo": customer.phone_number,  # استفاده از phone_number از Customer
            "firstName": customer.first_name,  # استفاده از first_name از Customer
            "lastName": customer.last_name,  # استفاده از last_name از Customer
            "nationalId": customer.national_id,  # استفاده از national_id از Customer
            "addressStatus": 1,  # وضعیت آدرس (مثلاً منزل)
            "postcode": request.data.get("postal_code"),
            "selfReportingAddress": request.data.get("street_address"),
            "buildingNumber": request.data.get("house_number"),
            "floor": request.data.get("floor"),
            "unit": request.data.get("unit_number")
        }

        # ارسال درخواست به API پستکس برای احراز آدرس
        response = requests.post(
            "https://api.postex.ir/api/v1/address-verify",
            json=address_data,
            headers={"Authorization": f"ApiKey {YOUR_API_KEY}"}
        )

        if response.status_code == 200:
            # آدرس تایید شد
            address = get_object_or_404(Address, id=kwargs["pk"], customer=customer)
            serializer = self.get_serializer(address, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "آدرس با موفقیت به‌روزرسانی شد.", "data": serializer.data},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "خطا در به‌روزرسانی آدرس.", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # اگر آدرس تایید نشد
            return Response(
                {"error": "آدرس وارد شده معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )
