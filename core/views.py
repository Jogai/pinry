import coreapi
import coreschema
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, routers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.viewsets import GenericViewSet
from taggit.models import Tag, TaggedItem

from core import serializers as api
from core.models import Image, Pin, Board
from core.permissions import IsOwnerOrReadOnly, OwnerOnlyIfPrivate
from core.serializers import filter_private_pin, filter_private_board


class ImageViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Image.objects.all()
    serializer_class = api.ImageSerializer

    def create(self, request, *args, **kwargs):
        return super(ImageViewSet, self).create(request, *args, **kwargs)


class PinViewSet(viewsets.ModelViewSet):
    serializer_class = api.PinSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ("submitter__username", 'tags__name', "pins__id")
    ordering_fields = ('-id', )
    ordering = ('-id', )
    permission_classes = [IsOwnerOrReadOnly("submitter"), OwnerOnlyIfPrivate("submitter")]

    def get_queryset(self):
        query = Pin.objects.all()
        request = self.request
        return filter_private_pin(request, query)

    @action(
        detail=True,
        methods=['get'],
        url_path='similar',
        schema=AutoSchema(manual_fields=[
            coreapi.Field(
                'limit',
                required=False,
                location='query',
                schema=coreschema.Integer(
                    description='Number of similar pins to return (max 48, default 12).',
                ),
            ),
        ]),
    )
    def similar(self, request, pk=None):
        """
        Returns pins most similar to this one, ranked by shared tag count.
        Private pins belonging to other users are excluded.
        """
        pin = self.get_object()
        tag_ids = list(pin.tags.values_list('id', flat=True))
        if not tag_ids:
            return Response({'results': [], 'next': None})

        limit = min(int(request.query_params.get('limit', 12)), 48)
        ct = ContentType.objects.get_for_model(Pin)

        similar_pin_ids = list(
            TaggedItem.objects
            .filter(tag_id__in=tag_ids, content_type=ct)
            .exclude(object_id=pin.id)
            .values('object_id')
            .annotate(shared=Count('tag_id'))
            .order_by('-shared')
            .values_list('object_id', flat=True)[:limit]
        )

        pins_qs = filter_private_pin(request, Pin.objects.filter(id__in=similar_pin_ids))
        id_order = {pid: i for i, pid in enumerate(similar_pin_ids)}
        pins_sorted = sorted(pins_qs, key=lambda p: id_order.get(p.id, 999))

        serializer = api.PinSerializer(pins_sorted, many=True, context={'request': request})
        return Response({'results': serializer.data, 'next': None})


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = api.BoardSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ("name", )
    filter_fields = ("submitter__username", )
    ordering_fields = ('-id', )
    ordering = ('-id', )
    permission_classes = [IsOwnerOrReadOnly("submitter"), OwnerOnlyIfPrivate("submitter")]

    def get_queryset(self):
        return filter_private_board(self.request, Board.objects.all())


class BoardAutoCompleteViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = api.BoardAutoCompleteSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ("submitter__username", )
    ordering_fields = ('-id', )
    ordering = ('-id', )
    pagination_class = None
    permission_classes = [OwnerOnlyIfPrivate("submitter"), ]

    def get_queryset(self):
        return filter_private_board(self.request, Board.objects.all())


class TagAutoCompleteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = api.TagAutoCompleteSerializer
    pagination_class = None

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super(TagAutoCompleteViewSet, self).list(
            request,
            *args,
            **kwargs
        )


class TagViewSet(viewsets.GenericViewSet):
    from core.permissions import SuperUserOnly
    queryset = Tag.objects.all()
    serializer_class = api.TagAutoCompleteSerializer
    permission_classes = [SuperUserOnly]

    from rest_framework.decorators import action
    from rest_framework.response import Response

    @action(detail=False, methods=['get', 'delete'], url_path='orphans')
    def orphans(self, request):
        from rest_framework.response import Response
        orphans = Tag.objects.filter(taggit_taggeditem_items=None)
        if request.method == 'GET':
            return Response({'count': orphans.count(), 'tags': list(orphans.values_list('name', flat=True))})
        deleted_names = list(orphans.values_list('name', flat=True))
        count = orphans.count()
        orphans.delete()
        return Response({'deleted': count, 'tags': deleted_names})


drf_router = routers.DefaultRouter()
drf_router.register(r'pins', PinViewSet, basename="pin")
drf_router.register(r'images', ImageViewSet)
drf_router.register(r'boards', BoardViewSet, basename="board")
drf_router.register(r'tags-auto-complete', TagAutoCompleteViewSet)
drf_router.register(r'boards-auto-complete', BoardAutoCompleteViewSet, basename="board")
drf_router.register(r'tags', TagViewSet, basename="tag")
