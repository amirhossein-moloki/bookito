from rest_framework import serializers
from .models import Publisher

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'established_date', 'address', 'website', 'email', 'phone_number', 'country', 'description', 'logo', 'social_media_links']
        read_only_fields = ['id']  # فیلد id فقط برای خواندن باشد
