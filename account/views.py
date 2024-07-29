import uuid

import requests
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.models import Social, User
from account.schemas import (
    list_schema_info,
    retrieve_schema_info,
    login_schema_info,
    wechat_mini_login_schema_info,
    profile_schema_info,
    wechat_profile_schema_info,
)
from account.serializers.serializers import (
    LoginRequestSerializer,
    WechatLoginRequestSerializer,
    LoginResponseSerializer,
    WechatProfilePostSerializer,
)
from account.serializers.model import UserSerializer
from account.utils.signinup import wristcheck_signinup
from dependency.oss_storage import OSSManager
from utils.pagination import CustomPagination
from utils.permission import CustomGetPermissionMixin, IsOwnerOrAdminUser
from wristcheck_api.settings import (
    env,
    OSS_ACCESS_KEY_ID,
    OSS_ACCESS_KEY_SECRET,
    OSS_ENDPOINT,
    OSS_BUCKET,
)


class UserViewSet(CustomGetPermissionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (
        BasicAuthentication,
        SessionAuthentication,
        TokenAuthentication,
    )
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        "list": [IsAdminUser],
        "retrieve": [IsOwnerOrAdminUser],
        "profile": [IsAuthenticated],
        "wechat_profile": [IsAuthenticated],
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["username", "email", "is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email"]
    ordering_fields = ["date_joined", "last_login"]
    ordering = ["-last_login"]

    @extend_schema(**list_schema_info)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**retrieve_schema_info)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**login_schema_info)
    @action(
        methods=["POST"], detail=False, authentication_classes=[], permission_classes=[]
    )
    def login(self, request, *args, **kwargs):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @extend_schema(**wechat_mini_login_schema_info)
    @action(
        methods=["POST"], detail=False, authentication_classes=[], permission_classes=[]
    )
    def wechat_mini_login(self, request, *args, **kwargs):
        serializer = WechatLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]
        wechat_data = requests.get(
            env.str("WECHAT_MINI_GET_SESSION_KEY_URL", ""),
            {
                "appid": env.str("WECHAT_MINI_APPID", ""),
                "secret": env.str("WECHAT_MINI_SECRET", ""),
                "js_code": code,
                "grant_type": "authorization_code",
            },
        ).json()
        open_id = wechat_data.get("openid")
        if not open_id:
            return Response(
                {"detail": "Can not get wechat openid"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        with transaction.atomic():
            social = Social.objects.filter(open_id=open_id).first()
            if not social:
                sign_res = wristcheck_signinup(open_id, wechat_data.get("session_key"))
                wristcheck_user_id = sign_res.get("user", {}).get("id")
                user = User.objects.create(
                    id=wristcheck_user_id,
                    username=str(uuid.uuid4()),
                )
                Social.objects.create(
                    **{
                        "user": user,
                        "open_id": open_id,
                    }
                )
            else:
                user = social.user
                user.last_login = timezone.now()
                user.save()

            token, _ = Token.objects.get_or_create(user=user)
            response_serializer = LoginResponseSerializer({"token": token.key})
            return Response(response_serializer.data)

    @extend_schema(**profile_schema_info)
    @action(methods=["GET"], detail=False)
    def profile(self, request):
        instance = User.objects.filter(id=request.user.id).first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(**wechat_profile_schema_info)
    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def wechat_profile(self, request, *args, **kwargs):
        """Update wechat profile, eg: avatar, nickname.
        At least one of 'nickname' or 'avatar_url' must be provided.
        """
        serializer = WechatProfilePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        avatar_url = validated_data.get("avatar_url")
        update_data = dict(nickname=validated_data.get("nickname", "微信匿名用户"))
        if avatar_url:
            manager = OSSManager(
                access_key_id=OSS_ACCESS_KEY_ID,
                access_key_secret=OSS_ACCESS_KEY_SECRET,
                endpoint=OSS_ENDPOINT,
                bucket_name=OSS_BUCKET,
                subdirectory="wechat-avatar",
            )
            res = manager.stream_upload_avatar_from_url(request.user.id, url=avatar_url)
            update_data.update(avatar_url=res["object_key"])

        Social.objects.filter(user=request.user, application_type="mp").update(
            **update_data
        )
        return Response(status=status.HTTP_200_OK)
