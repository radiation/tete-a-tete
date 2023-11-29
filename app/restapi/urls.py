from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from django.urls import path
from .views import *

urlpatterns = [

    path("register/", RegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    #path("user/", UserDetailsView.as_view(), name="rest_user_details"),

    path('user/', UserListCreateView.as_view(), name='user-list-create'),
    path('user/create/', UserListCreateView.as_view(), name='user-create'),
    path('user/id/<int:id_value>', UserListByIDView.as_view(), name='user-by-id'),

    path('meeting/', MeetingListView.as_view(), name='meeting-list'),
    path('meeting/create/', MeetingCreateView.as_view(), name='meeting-create'),
    path('meeting/id/<int:id_value>', MeetingListByIDView.as_view(), name='meeting-list-by-id'),
    path('meeting/user/<int:user_id_value>', MeetingListByUserView.as_view(), name='meeting-list-by-user'),

    path('actionitem/', ActionItemListView.as_view(), name='actionitem-list'),
    path('actionitem/create/', ActionItemCreateView.as_view(), name='actionitem-create'),
    path('actionitem/user/<int:user_id_value>', ActionItemListByUserView.as_view(), name='actionitem-list-by-user'),
    path('actionitem/meeting/<int:meeting_id_value>', ActionItemListByMeetingView.as_view(), name='actionitem-list-create'),

    path('question/', QuestionListView.as_view(), name='question-list'),
    path('question/create/', QuestionCreateView.as_view(), name='question-create'),
    path('question/id/<int:id_value>', QuestionListByIDView.as_view(), name='question-list-by-id'),

    path('questionanswer/', QuestionAnswerListView.as_view(), name='questionanswer-list'),
    path('questionanswer/create/', QuestionAnswerCreateView.as_view(), name='questionanswer-create'),
    path('questionanswer/id/<int:id_value>', QuestionAnswerListByIDView.as_view(), name='questionanswer-by-id'),    

    path('agendaitem/', AgendaItemListView.as_view(), name='agendaitem-list'),
    path('agendaitem/create/', AgendaItemCreateView.as_view(), name='agendaitem-create'),
    path('agendaitem/meeting/<int:meeting_id_value>', AgendaItemListByMeetingView.as_view(), name='agendaitem-list-by-meeting'),
    path('agendaitem/id/<int:id_value>', AgendaItemListByIDView.as_view(), name='agendaitem-list-by-id'),
    
]
