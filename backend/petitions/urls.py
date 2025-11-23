from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetitionViewSet

router = DefaultRouter()
router.register(r'petitions', PetitionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
