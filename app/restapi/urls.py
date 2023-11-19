from django.urls import path
from .views import *

urlpatterns = [
    path('user/', UserListCreateView.as_view(), name='user-list-create'),
    path('user/id/<int:id_value>', UserListByIDView.as_view(), name='user-list-create'),
    path('user/create/', UserListCreateView.as_view(), name='user-create'),

    path('meeting/', MeetingListCreateView.as_view(), name='meeting-list-create'),
    path('meeting/create/', MeetingListCreateView.as_view(), name='meeting-create'),
    path('meeting/user/<int:user_id_value>', MeetingListByUserView.as_view(), name='meeting-list-create'),

    path('actionitem/', UserListCreateView.as_view(), name='actionitem-list-create'),
    path('actionitem/create/', ActionItemListCreateView.as_view(), name='actionitem-create'),
    path('actionitem/user/<int:user_id_value>', ActionItemListByUserView.as_view(), name='actionitem-list-create'),
    path('actionitem/meeting/<int:meeting_id_value>', ActionItemListByUserView.as_view(), name='actionitem-list-create'),
]
