from django.urls import path
from .views import AdaptRoleView

urlpatterns = [
    path('adapt-role/', AdaptRoleView.as_view(), name='adapt-role'),
]