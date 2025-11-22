from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import (
    ChatMessageViewSet,
    CompanyViewSet,
    ContactViewSet,
    CrmTagViewSet,
    DealViewSet,
    LeadViewSet,
    MemoViewSet,
    ProjectStageViewSet,
    ProjectViewSet,
    StageViewSet,
    TaskStageViewSet,
    TaskTagViewSet,
    CallLogViewSet,
    TaskViewSet,
    UserViewSet,
    dashboard_analytics,
    dashboard_activity,
)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('tasks', TaskViewSet, basename='task')
router.register('projects', ProjectViewSet, basename='project')
router.register('deals', DealViewSet, basename='deal')
router.register('leads', LeadViewSet, basename='lead')
router.register('companies', CompanyViewSet, basename='company')
router.register('contacts', ContactViewSet, basename='contact')
router.register('memos', MemoViewSet, basename='memo')
router.register('chat-messages', ChatMessageViewSet, basename='chat-message')
router.register('stages', StageViewSet, basename='stage')
router.register('task-stages', TaskStageViewSet, basename='task-stage')
router.register('project-stages', ProjectStageViewSet, basename='project-stage')
router.register('crm-tags', CrmTagViewSet, basename='crm-tag')
router.register('task-tags', TaskTagViewSet, basename='task-tag')
router.register('call-logs', CallLogViewSet, basename='calllog')

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='api:schema'),
        name='docs',
    ),
    path('auth/token/', obtain_auth_token, name='api-token'),
    path('dashboard/analytics/', dashboard_analytics, name='dashboard-analytics'),
    path('dashboard/activity/', dashboard_activity, name='dashboard-activity'),
    path('', include(router.urls)),
]
