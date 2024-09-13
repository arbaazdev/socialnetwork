from rest_framework import serializers
from .models import User, FriendRequest
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError


class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user signup. Validates the email and password and creates a new user.
    """

    class Meta:
        model = User
        fields = ['email', 'name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Override the create method to handle password hashing.

        Args:
            validated_data (dict): Validated data for creating a user.

        Returns:
            User: The created user object.
        """
        user = User(
            email=validated_data['email'].lower(),
            name=validated_data['name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Validates the provided email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the email and password. Authenticates the user.

        Args:
            data (dict): Email and password.

        Returns:
            dict: The validated data.
        """
        email = data.get('email').lower()
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class for the User model. Transforms User objects into JSON format.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Serializer class for the FriendRequest model. Transforms FriendRequest objects into JSON format.
    """

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ['id', 'from_user', 'created_at']

    def to_representation(self, instance):
        """
        Override the default representation to use nested serializers for `from_user` and `to_user`.
        """
        representation = super().to_representation(instance)
        representation['from_user'] = UserSerializer(instance.from_user).data
        representation['to_user'] = UserSerializer(instance.to_user).data
        return representation

    def validate(self, attrs):
        """
        Override the default validate method to set the `from_user` field to the requesting user
        and ensure that the request is not a duplicate.

        Args:
            attrs (dict): The data to validate.

        Returns:
            dict: The validated data with `from_user` set to the requesting user.
        """

        from_user = self.context['request'].user
        to_user = attrs.get('to_user')

        if from_user == to_user:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")

        # Check if a similar request already exists
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already exists.")

        validated_data = super().validate(attrs)
        validated_data['from_user'] = from_user
        return validated_data


    def update(self, instance, validated_data):
        """
        Update and return an existing FriendRequest instance.
        """
        request = self.context.get('request')
        user = request.user

        # Ensure that the user is the recipient of the friend request
        if instance.to_user != user:
            raise ValidationError("You can only accept or reject requests sent to you.")

        # Update the status
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
