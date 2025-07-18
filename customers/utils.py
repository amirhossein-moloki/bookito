import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PostexShippingAPI:
    """
    کلاس واسط برای ارتباط با API پستکس جهت محاسبه هزینه ارسال.
    """

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')  # حذف اسلش انتهایی در صورت وجود

    def calculate_shipping_cost(self, weight, from_city, to_city, package_type='standard'):
        # فرض شده مسیر محاسبه هزینه ارسال '/calculate' است؛ بسته به مستندات API این مسیر ممکن است تغییر کند
        url = f"{self.base_url}/calculate"
        payload = {
            "weight": weight,
            "from_city": from_city,
            "to_city": to_city,
            "package_type": package_type
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # در صورت بروز خطای HTTP exception ایجاد می‌کند
        data = response.json()
        shipping_cost = data.get("shipping_cost")
        if shipping_cost is None:
            raise Exception("Shipping cost not provided in response")
        return shipping_cost


class CalculatePostexShippingView(APIView):
    """
    ویو API برای محاسبه هزینه ارسال کالا با استفاده از API پستکس.
    ورودی‌ها (از طریق پارامترهای query) شامل:
      - weight: وزن کالا (به عنوان عدد)
      - from_city: شهر مبدا
      - to_city: شهر مقصد
      - package_type: (اختیاری) نوع بسته‌بندی، به صورت پیش‌فرض 'standard'
    """

    def get(self, request, *args, **kwargs):
        weight = request.query_params.get("weight")
        from_city = request.query_params.get("from_city")
        to_city = request.query_params.get("to_city")
        package_type = request.query_params.get("package_type", "standard")

        if not weight or not from_city or not to_city:
            return Response(
                {"error": "Missing required parameters: weight, from_city, to_city"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            weight = float(weight)
        except ValueError:
            return Response({"error": "Invalid weight value"}, status=status.HTTP_400_BAD_REQUEST)

        api_key = settings.POSTEX_API_KEY
        base_url = settings.POSTEX_BASE_URL

        postex_api = PostexShippingAPI(api_key, base_url)
        try:
            cost = postex_api.calculate_shipping_cost(weight, from_city, to_city, package_type)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"shipping_cost": cost}, status=status.HTTP_200_OK)

import requests

def calculate_shipping_cost(from_city_code, to_city_code, cart_total, cart_weight, api_key):
    url = "https://api.postex.ir/api/v1/shipping/quotes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # کلید API برای احراز هویت
    }

    data = {
        "from_city_code": from_city_code,
        "pickup_needed": True,
        "courier": {
            "courier_code": "POSTEX",
            "service_type": "STANDARD"
        },
        "parcels": [
            {
                "custom_parcel_id": "123456",
                "to_city_code": to_city_code,
                "payment_type": "PREPAID",  # پرداخت آنلاین
                "parcel_properties": {
                    "length": 30,  # مقدار پیش‌فرض (قابل تغییر)
                    "width": 20,
                    "height": 15,
                    "total_weight": cart_weight,
                    "is_fragile": False,
                    "is_liquid": False,
                    "total_value": cart_total,
                    "pre_paid_amount": cart_total,
                    "total_value_currency": "IRR",
                    "box_type_id": 1
                }
            }
        ],
        "value_added_service": {
            "request_packaging": True,
            "request_sms_notification": True,
            "request_email_notification": True
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        shipping_info = response.json()
        return shipping_info  # برگرداندن اطلاعات هزینه ارسال از API
    else:
        return {"error": response.status_code, "message": response.text}
