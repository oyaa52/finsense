from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    subscribed_products = serializers.CharField()

    def get_cleaned_data(self):
        data =  super().get_cleaned_data()
        data['subscribed_products'] = self.validated_data.get('subscribed_products')
        return data
    
    def save(self, request):
        user = super().save(request)
        user.subscribed_products = self.validated_data.get('subscribed_products')
        user.save()
        return user