import requests
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from customers.models import Customer
from .models import Address
from .serializers import AddressSerializer

YOUR_API_KEY = 'postex_5ea5656aa6014bcROOGfLeIN9rQY6uZTXehFd95hQyB2Z'

class AddressViewSet(viewsets.ModelViewSet):
    """
    این ViewSet فقط آدرس مرتبط با Customer فعلی را نمایش و مدیریت می‌کند.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        فقط آدرس متعلق به Customer مرتبط با کاربر درخواست‌دهنده را برمی‌گرداند.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        if customer.address:
            return Address.objects.filter(id=customer.address.id)
        return Address.objects.none()

    def create(self, request, *args, **kwargs):
        """
        در متد create کل منطق ایجاد آدرس و ارتباط آن با Customer قرار می‌گیرد.
        """
        customer = get_object_or_404(Customer, user=request.user)

        # آماده‌سازی داده‌ها جهت احراز آدرس
        address_data = {
            "cellPhoneNo": customer.phone_number,      # استفاده از phone_number از Customer
            "firstName": customer.first_name,            # استفاده از first_name از Customer
            "lastName": customer.last_name,              # استفاده از last_name از Customer
            "nationalId": customer.national_id,          # استفاده از national_id از Customer
            "addressStatus": 1,                          # وضعیت آدرس (مثلاً منزل)
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
            # آدرس تایید شد: ابتدا داده‌های ورودی رو اعتبارسنجی می‌کنیم
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # ذخیره آدرس جدید
            address = serializer.save()
            # اختصاص دادن آدرس به Customer
            customer.address = address
            customer.save()
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"message": "آدرس جدید با موفقیت ایجاد شد.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        else:
            # در صورت عدم تایید آدرس توسط API
            return Response(
                {"error": "آدرس وارد شده معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        حذف آدرس تنها در صورتی امکان‌پذیر است که آدرس متعلق به Customer جاری باشد.
        """
        customer = get_object_or_404(Customer, user=request.user)
        address = customer.address
        if address and str(address.id) == str(kwargs["pk"]):
            address.delete()
            customer.address = None
            customer.save()
            return Response(
                {"message": "آدرس با موفقیت حذف شد."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"error": "آدرس یافت نشد یا دسترسی غیرمجاز."},
            status=status.HTTP_404_NOT_FOUND
        )

    def update(self, request, *args, **kwargs):
        """
        ویرایش آدرس تنها در صورتی امکان‌پذیر است که آدرس متعلق به Customer جاری باشد.
        """
        customer = get_object_or_404(Customer, user=request.user)
        address = customer.address
        if not address or str(address.id) != str(kwargs["pk"]):
            return Response(
                {"error": "آدرس یافت نشد یا دسترسی غیرمجاز."},
                status=status.HTTP_404_NOT_FOUND
            )

        address_data = {
            "cellPhoneNo": customer.phone_number,      
            "firstName": customer.first_name,            
            "lastName": customer.last_name,              
            "nationalId": customer.national_id,          
            "addressStatus": 1,                          
            "postcode": request.data.get("postal_code"),
            "selfReportingAddress": request.data.get("street_address"),
            "buildingNumber": request.data.get("house_number"),
            "floor": request.data.get("floor"),
            "unit": request.data.get("unit_number")
        }

        response = requests.post(
            "https://api.postex.ir/api/v1/address-verify",
            json=address_data,
            headers={"Authorization": f"ApiKey {YOUR_API_KEY}"}
        )

        if response.status_code == 200:
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
            return Response(
                {"error": "آدرس وارد شده معتبر نیست."},
                status=status.HTTP_400_BAD_REQUEST
            )
