from ckeditor import fields
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt import serializers as rest_framework_simplejwt_serializers
from rest_framework_simplejwt.serializers import TokenVerifySerializer

from app import models
from app.models import Position

UserModel = get_user_model()


class FlowModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Flow
        # fields = '__all__'
        exclude = ()


class StaffModelSerializer(serializers.ModelSerializer):
    position = serializers.CharField(source='position.name', read_only=True)
    company = serializers.CharField(source='company.name', read_only=True)
    group_name = serializers.CharField(source='group_name.name', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = models.Staff
        exclude = ()


class JWTTokenObtainSerializer(rest_framework_simplejwt_serializers.TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class JWTTokenVerifySerializer(rest_framework_simplejwt_serializers.TokenVerifySerializer):

    def validate(self, attrs):
        data = rest_framework_simplejwt_serializers.UntypedToken(attrs['token'])
        user_id = data.payload.get('user_id', False)
        valid_data = TokenVerifySerializer().validate(data)
        user = models.Staff.objects.get(id=user_id)

        user_serializers = StaffModelSerializer(user)
        return {
            'status': 'success',
            'data': {
                "valid": True,
                "user": user_serializers.data
            },
        }
