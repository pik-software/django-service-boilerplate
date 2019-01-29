from rest_framework import renderers, serializers, permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=200)


class StandardizedUserApiView(APIView):
    throttle_classes = ()
    permission_classes = (permissions.IsAuthenticated, )
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user,
                                           context={'request': request})
        return Response(serializer.data)


USER_API_VIEW = StandardizedUserApiView.as_view()
