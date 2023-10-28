import countryinfo
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers
from . import validators


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "date_joined",
            "referrer_id",
            "is_verified",
            "is_online",
        ]

        ref_name = "Base User"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class UserSerializer:
    class List(serializers.ModelSerializer):
        class Meta:
            model = get_user_model()
            fields = [
                "id",
                "first_name",
                "last_name",
                "username",
                "email",
                "date_joined",
                "account_type",
                "referrer_id",
            ]
            ref_name = "User - List"

    class AdminList(serializers.ModelSerializer):
        groups = GroupSerializer(read_only=True, many=True)

        class Meta:
            model = get_user_model()
            fields = [
                "id",
                "first_name",
                "last_name",
                "username",
                "email",
                "date_joined",
                "account_type",
                "referrer_id",
            ]
            ref_name = "Admin - List"

    class LivingInLocation(serializers.Serializer):
        country = serializers.CharField(
            allow_null=False, allow_blank=False, max_length=128, required=True
        )
        state = serializers.CharField(
            allow_null=False, allow_blank=False, max_length=128, required=True
        )

        def validate_country(self, value):
            try:
                country = countryinfo.CountryInfo((value or "").strip())
                return country.info()["name"]
            except KeyError:
                message = f"'{value}' is not a valid country"
                raise serializers.ValidationError(message, "invalid country")

        def validate_state(self, value):
            return (value or "").strip().title()

        class Meta:
            validators = [validators.CountryStateValidator()]


    class Update(serializers.ModelSerializer):
        username = serializers.CharField(
            allow_blank=False,
            allow_null=True,
            max_length=150,
        )
        living_in = serializers.JSONField(required=False, allow_null=True)

        def validate_living_in(self, data):
            serializer = UserSerializer.LivingInLocation(data=data)
            serializer.is_valid(raise_exception=True)
            return serializer.validated_data


        @staticmethod
        def validate_dob(value):
            validators.DOBValidator()(value)
            return value

        class Meta:
            model = get_user_model()
            fields = [
                "first_name",
                "last_name",
                "email",
                "username",
                "is_email_verified",
                "city",
                "country",
                "gender",
                "referrer_id",
                "is_invited",
                "invited_by",
                "is_supended",
                "suspend_duration_in_minutes",
                "dob",
                "living_in",
                "device_token_registration",
            ]

            ref_name = "User - Update"

    class Retrieve(serializers.ModelSerializer):
        invited_by = BaseUserSerializer(read_only=True)
        class Meta:
            model = get_user_model()
            exclude = [
                "password",
                "is_superuser",
                "is_staff",
                "is_active",
                "groups",
                "user_permissions",
                "old_passwords",
                "google_auth_credentials",
            ]

            ref_name = "User - Retrieve"

    class WalletBalance(serializers.ModelSerializer):
        class Meta:
            model = get_user_model()
            fields = ["id", "username", "wallet_balance"]
            ref_name = "User - Wallet Balance"


class AdminUserSerializer:
    class Create(UserSerializer.Update):
        invited_by = serializers.PrimaryKeyRelatedField(
            queryset=get_user_model().objects, many=False
        )

        class Meta:
            model = get_user_model()
            fields = ["email", "invited_by", "account_type", "is_email_verified"]
            ref_name = "User - Admin"


