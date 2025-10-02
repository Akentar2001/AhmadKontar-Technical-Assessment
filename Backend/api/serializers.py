from rest_framework import serializers
from .models import User, Grocery, Item, DailyIncome

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_staff=validated_data.get('is_staff', False)
        )
        return user

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class DailyIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyIncome
        fields = '__all__'
        read_only_fields = ('grocery', 'created_at', 'updated_at')

class GrocerySerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)
    incomes = DailyIncomeSerializer(many=True, read_only=True)

    class Meta:
        model = Grocery
        fields = ['id', 'name', 'location', 'responsible_person', 'items', 'incomes', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')