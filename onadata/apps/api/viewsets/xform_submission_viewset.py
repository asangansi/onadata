# -*- coding=utf-8 -*-
"""
XFormSubmissionViewSet module
"""
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.conf import settings
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           TokenAuthentication)
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from onadata.apps.api.permissions import IsAuthenticatedSubmission
from onadata.apps.api.tools import get_baseviewset_class
from onadata.apps.logger.models import Instance
from onadata.libs import filters
from onadata.libs.authentication import (DigestAuthentication,
                                         EnketoTokenAuthentication)
from onadata.libs.mixins.authenticate_header_mixin import \
    AuthenticateHeaderMixin
from onadata.libs.mixins.openrosa_headers_mixin import OpenRosaHeadersMixin
from onadata.libs.renderers.renderers import TemplateXMLRenderer, FLOIPRenderer
from onadata.libs.serializers.data_serializer import (
    JSONSubmissionSerializer, RapidProSubmissionSerializer,
    SubmissionSerializer, FLOIPSubmissionSerializer)

BaseViewset = get_baseviewset_class()  # pylint: disable=C0103

# 10,000,000 bytes
DEFAULT_CONTENT_LENGTH = getattr(settings, 'DEFAULT_CONTENT_LENGTH', 10000000)


class FLOIPParser(JSONParser):
    media_type = 'application/vnd.org.flowinterop.results+json'
    renderer_classes = FLOIPRenderer


class XFormSubmissionViewSet(AuthenticateHeaderMixin,  # pylint: disable=R0901
                             OpenRosaHeadersMixin,
                             mixins.CreateModelMixin,
                             BaseViewset,
                             viewsets.GenericViewSet):
    """
    XFormSubmissionViewSet class
    """
    authentication_classes = (DigestAuthentication, BasicAuthentication,
                              TokenAuthentication, EnketoTokenAuthentication)
    filter_backends = (filters.AnonDjangoObjectPermissionFilter, )
    model = Instance
    permission_classes = (permissions.AllowAny, IsAuthenticatedSubmission)
    renderer_classes = (FLOIPRenderer, TemplateXMLRenderer, JSONRenderer,
                        BrowsableAPIRenderer)
    serializer_class = SubmissionSerializer
    template_name = 'submission.xml'
    parser_classes = (FLOIPParser, JSONParser, FormParser, MultiPartParser)

    def get_serializer(self, *args, **kwargs):
        """
        Pass many=True flag if data is a list.
        """
        if "data" in kwargs:
            data = kwargs["data"]

            if isinstance(data, list):
                kwargs["many"] = True
        return super(XFormSubmissionViewSet, self).get_serializer(*args, **kwargs)

    def get_serializer_class(self):
        """
        Returns the serializer class to be used based on content_type.
        """
        content_type = self.request.content_type.lower()

        if 'application/json' in content_type:
            self.request.accepted_renderer = JSONRenderer()
            self.request.accepted_media_type = 'application/json'

            return JSONSubmissionSerializer

        if 'application/x-www-form-urlencoded' in content_type:
            return RapidProSubmissionSerializer

        if 'application/vnd.org.flowinterop.results+json' in content_type:
            self.request.accepted_renderer = FLOIPRenderer()
            self.request.accepted_media_type = 'application/vnd.org.flowinterop.results+json'

            return FLOIPSubmissionSerializer

        return SubmissionSerializer

    def create(self, request, *args, **kwargs):
        if request.method.upper() == 'HEAD':
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                template_name=self.template_name)

        return super(XFormSubmissionViewSet, self).create(
            request, *args, **kwargs)

    def handle_exception(self, exc):
        """
        Handles exceptions thrown by handler method and
        returns appropriate error response.
        """
        if hasattr(exc, 'response'):
            return exc.response
        return super(XFormSubmissionViewSet, self).handle_exception(exc)
