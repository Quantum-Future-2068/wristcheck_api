from decouple import config
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.models import Social
from account.serializer import UserSerializer
from drf.pagination import CustomPagination
from wristcheck_api.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from wristcheck_api.permission import GetPermissionByModelActionMixin, IsOwnerOrAdminUser


class UserViewSet(
    GetPermissionByModelActionMixin,
    viewsets.ReadOnlyModelViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (
        SessionAuthentication,
        TokenAuthentication
    )
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsOwnerOrAdminUser],
        'profile': [IsAuthenticated]
    }
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['username', 'email', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'last_login']
    ordering = ['-last_login']

    @extend_schema(
        summary='user_list',
        description='**PERMISSION**: Allows access only to admin users.',
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Which field to use when ordering the results. default: -last_login',
                enum=['date_joined', 'last_login'],
                required=False
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description=f'Number of results to return per page. Maximum value is {DEFAULT_MAX_PAGE_SIZE}.',
                required=False,
                default=DEFAULT_PAGE_SIZE,
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description=f'Filter results by **username** or **email**. ',
                required=False,
            )
        ],
        responses={
            200: OpenApiResponse(
                response=serializer_class(many=True),
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='user_retrieve',
        description='**PERMISSION**: Allows access only to owner or admin users.'
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['user'],
        summary='user_login',
        description='Login with username and password and return a token',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {
                        'type': 'string',
                        'example': 'admin'
                    },
                    'password': {
                        'type': 'string',
                        'example': 'admin'
                    }
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {
                        'type': 'string',
                        'example': 'token string'
                    }
                }
            },
            401: {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid credentials'
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Login Request',
                summary='An example of a login request payload',
                value={'username': 'admin', 'password': 'admin'},
                request_only=True
            ),
            OpenApiExample(
                'Login Response',
                summary='An example of a successful login response',
                value={'token': 'token string'},
                response_only=True
            ),
            OpenApiExample(
                'Login Error Response',
                summary='An example of an error response due to invalid credentials',
                value={'error': 'Invalid credentials'},
                response_only=True
            )
        ]
    )
    @action(methods=['POST'], detail=False, authentication_classes=[], permission_classes=[])
    def login(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema(
        tags=['user'],
        summary='wechat_mini_login',
        description='Login with code and return a token',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'code': {
                        'type': 'string',
                        'example': 'code'
                    },
                },
                'required': ['code']
            }
        },
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'token': {
                            'type': 'string',
                            'example': 'token string'
                        }
                    }
                },
                description='Successful Response'
            ),
            400: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Code is required'
                        }
                    }
                },
                description='Code is required'
            ),
            401: OpenApiResponse(response={
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Can not get wechat open_id'
                    }
                }
            }, description='Can not get wechat open_id'),
        },
        examples=[
            OpenApiExample(
                'Login Request',
                summary='An example of a login request payload',
                value={'code': 'code'},
                request_only=True
            ),
            OpenApiExample(
                'Login Response',
                summary='An example of a successful login response',
                value={'token': 'token string'},
                response_only=True
            ),
            OpenApiExample(
                'Login Error Response1',
                summary='An example of an error response due to missing code',
                value={'error': 'Code is required'},
                response_only=True
            ),
            OpenApiExample(
                'Login Error Response2',
                summary='An example of an error response due to invalid credentials',
                value={'error': 'Can not get wechat open_id'},
                response_only=True
            )
        ]
    )
    @action(methods=['POST'], detail=False, authentication_classes=[], permission_classes=[])
    def wechat_mini_login(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        wechat_data = requests.get(
            config('WECHAT_MINI_GET_SESSION_KEY_URL'),
            {
                "appid": config('WECHAT_MINI_APPID'),
                "secret": config('WECHAT_MINI_SECRET'),
                "js_code": code,
                "grant_type": "authorization_code",
            },
        ).json()
        open_id = wechat_data.get('openid')
        if not open_id:
            return Response({'error': 'Can not get wechat open_id'}, status=status.HTTP_401_UNAUTHORIZED)

        social = Social.objects.filter(open_id=open_id).first()
        if not social:
            user = User.objects.create(username=wechat_data.get('nickname', ''))
            Social.objects.create(open_id=open_id, defaults={
                'user': user,
                'open_id': open_id,
                'nickname': wechat_data.get('nickname', ''),
                'avatar_url': wechat_data.get('avatar_url', '')
            })
        else:
            user = social.user

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @extend_schema(
        tags=['user'],
        summary='user_profile',
        description='Retrieve the profile of the authenticated user',
        responses={
            200: OpenApiResponse(
                response=serializer_class(many=False),
                description='Successful Response'
            ),
            401: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Authentication credentials were not provided.'
                        }
                    }
                },
                description='Authentication credentials were not provided.'
            )
        },
        examples=[
            OpenApiExample(
                'Profile Response',
                summary='An example of a successful profile response',
                value=serializer_class(many=False).data,
                response_only=True
            ),
            OpenApiExample(
                'Unauthorized Response',
                summary='An example of an unauthorized response',
                value={'error': 'Authentication credentials were not provided.'},
                response_only=True
            )
        ]
    )
    @action(methods=['GET'], detail=False)
    def profile(self, request):
        instance = User.objects.filter(id=request.user.id).first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
