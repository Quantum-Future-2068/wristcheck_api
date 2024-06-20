# tests/test_views.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

import factory

from account.tests import UserFactory
from track.models import WatchVisitRecord


class WatchVisitRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WatchVisitRecord

    user_id = factory.Faker('random_int', min=1, max=1000)  # Example range, adjust as needed
    watch_id = factory.Sequence(lambda n: f'watch-{n}')


@pytest.mark.django_db
class TestWatchVisitRecordViewSet:
    list_url = reverse('watchvisitrecord-list')  # adjust URL name if necessary

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.admin_user.set_password('password')
        self.admin_user.save()
        self.admin_user_watch = WatchVisitRecordFactory(user_id=self.admin_user.id, watch_id='watch_id_1')
        self.normal_user = UserFactory(is_staff=False, is_superuser=False)
        self.normal_user.set_password('password')
        self.normal_user.save()
        self.normal_user_watch = WatchVisitRecordFactory(user_id=self.normal_user.id, watch_id='watch_id_1')

    def test_list_endpoint_successful(self):
        self.client.login(username=self.admin_user.username, password='password')
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_endpoint_successful(self):
        self.client.login(username=self.admin_user.username, password='password')
        detail_url = reverse('watchvisitrecord-detail', kwargs={'pk': self.normal_user_watch.id})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK

    def test_destroy_endpoint_successful(self):
        self.client.login(username=self.admin_user.username, password='password')
        detail_url = reverse('watchvisitrecord-detail', kwargs={'pk': self.normal_user_watch.id})
        response = self.client.delete(detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_add_endpoint_successful(self):
        self.client.login(username=self.admin_user.username, password='password')
        data = {
            'watch_id': '123'
        }
        response = self.client.post(reverse('watchvisitrecord-add'), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_my_own_endpoint_successful(self):
        self.client.login(username=self.normal_user.username, password='password')
        response = self.client.get(reverse('watchvisitrecord-my-own'))
        assert response.status_code == status.HTTP_200_OK

    def test_analytics_endpoint_successful(self):
        self.client.login(username=self.admin_user.username, password='password')
        response = self.client.get(reverse('watchvisitrecord-analytics'), {'period': 'month'})
        assert response.status_code == status.HTTP_200_OK

    def test_list_endpoint_forbidden(self):
        self.client.login(username=self.normal_user.username, password='password')
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_endpoint_forbidden(self):
        self.client.login(username=self.normal_user.username, password='password')
        detail_url = reverse('watchvisitrecord-detail', kwargs={'pk': self.admin_user_watch.id})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_endpoint_forbidden(self):
        self.client.login(username=self.normal_user.username, password='password')
        detail_url = reverse('watchvisitrecord-detail', kwargs={'pk': self.admin_user_watch.id})
        response = self.client.delete(detail_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analytics_endpoint_forbidden(self):
        self.client.login(username=self.normal_user.username, password='password')
        response = self.client.get(reverse('watchvisitrecord-analytics'), {'period': 'month'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_endpoint_unauthenticated(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_endpoint_unauthenticated(self):
        detail_url = reverse('watchvisitrecord-detail', kwargs={'pk': self.admin_user_watch.id})
        response = self.client.get(detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_destroy_endpoint_unauthenticated(self):
        detail_url = reverse('watchvisitrecord-detail', kwargs={'pk': self.admin_user_watch.id})
        response = self.client.delete(detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_endpoint_unauthenticated(self):
        data = {
            'watch_id': '123'
        }
        response = self.client.post(reverse('watchvisitrecord-add'), data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_my_own_endpoint_unauthenticated(self):
        response = self.client.get(reverse('watchvisitrecord-my-own'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_analytics_endpoint_unauthenticated(self):
        response = self.client.get(reverse('watchvisitrecord-analytics'), {'period': 'month'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
