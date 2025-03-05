from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'province', 'province_code', 'city', 'city_code', 'street_address', 'house_number', 'postal_code', 'floor', 'unit_number', 'residence_type']
