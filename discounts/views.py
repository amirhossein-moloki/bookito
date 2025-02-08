from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Discount
from .serializers import DiscountSerializer
from django.utils import timezone

# 1. ایجاد تخفیف (فقط ادمین)
class DiscountCreateView(generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به ایجاد تخفیف هستند

# 2. ویرایش تخفیف (فقط ادمین)
class DiscountUpdateView(generics.UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به ویرایش تخفیف هستند

# 3. حذف تخفیف (فقط ادمین)
class DiscountDeleteView(generics.DestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdminUser]  # فقط ادمین‌ها مجاز به حذف تخفیف هستند

# 4. مشاهده لیست تخفیف‌ها (فقط کاربران احراز هویت‌شده)
class DiscountListView(generics.ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت‌شده می‌توانند لیست را ببینند

# 5. بررسی اعتبار کد تخفیف
class DiscountValidateView(generics.GenericAPIView):
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated]  # فقط کاربران احراز هویت‌شده مجاز به بررسی تخفیف هستند

    def get(self, request, *args, **kwargs):
        code = self.request.query_params.get('code', None)
        if not code:
            return Response({"error": "لطفاً کد تخفیف را وارد کنید."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            discount = Discount.objects.get(code=code)
            if discount.is_valid():
                return Response({
                    "success": "کد تخفیف معتبر است.",
                    "discount": discount.percentage,
                    "valid_until": discount.end_date
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "کد تخفیف معتبر نیست یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)
        except Discount.DoesNotExist:
            return Response({"error": "کد تخفیف یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
