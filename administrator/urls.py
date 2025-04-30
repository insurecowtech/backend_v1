from django.urls import path
from .views import *

app_name = 'administrator'
urlpatterns = [
    path('create-user/', CreateUserByAdminView.as_view(), name='admin-create-user'),
    path('users/<int:pk>/set-managed-by/', SetManagedByView.as_view(), name='set-managed-by'),
    path('users/list/', UserListView.as_view(), name='user-list'),
]
