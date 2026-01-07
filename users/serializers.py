from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


# ---------------- REGISTER SERIALIZER ----------------

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password", "role"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(
            **validated_data,
            is_active=False
        )
        user.set_password(password)
        user.save()
        return user
    
    

# ---------------- LOGIN SERIALIZER ----------------

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        # 1️⃣ Check if user exists first
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or password")

        # 2️⃣ Check admin approval
        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is pending admin approval"
            )

        # 3️⃣ Authenticate password
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password")

        data["user"] = user
        return data



# ------------------------- Staff List Serializer -------------------------
class StaffListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'date_joined',
            'phone',             
            'location', 
            'is_active',
        ]
        read_only_fields = fields

# ------------------------- Staff Detail Serializer -------------------------
class StaffDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'team',
            'date_joined',
            'last_login',
            'is_active',
            'phone',              
            'location', 
        ]
        read_only_fields = ['date_joined', 'last_login']

# ------------------------- Staff Create/Update Serializer -------------------------
class StaffCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'team',
            'is_active',
            'password',
            'phone',              
            'location', 
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
