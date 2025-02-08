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

def calculate_shipping_cost():
    return 0  # مقدار پیش‌فرض تا وقتی که نحوه محاسبه را مشخص کنید
