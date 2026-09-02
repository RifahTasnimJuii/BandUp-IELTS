from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.common.permissions import IsAdminUser, IsContentEditor
from .models import AudioAsset, Passage, Section, Test
from .serializers import AudioAssetSerializer, PassageSerializer, SectionSerializer, TestSerializer


class AdminTestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
      
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['list', 'retrieve']:
            
            if self.request.user.is_authenticated and (
                self.request.user.is_superuser or 
                self.request.user.role in ['admin', 'superadmin', 'content_editor']
            ):
                return queryset
            
            return queryset.filter(is_published=True)
        return queryset


class AdminSectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]


class AdminPassageViewSet(viewsets.ModelViewSet):
    queryset = Passage.objects.all()
    serializer_class = PassageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]


class AdminAudioAssetViewSet(viewsets.ModelViewSet):
    queryset = AudioAsset.objects.all()
    serializer_class = AudioAssetSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]