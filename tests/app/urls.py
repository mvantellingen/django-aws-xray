from django.conf.urls import url

from tests.app import views


urlpatterns = [
    url(r'', views.dummy_view)
]
