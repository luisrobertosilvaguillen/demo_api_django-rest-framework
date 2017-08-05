from negocios_exchange.models import User_Profile
from django.contrib.auth.models import User
from negocios_exchange.serializers import User_ProfileSerializer, CUserSerializer, CGroupSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from oauth2_provider.models import AccessToken, Application
from braces.views import CsrfExemptMixin
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.settings import oauth2_settings
from rest_framework import permissions
import json
class LoginView(APIView, CsrfExemptMixin, OAuthLibMixin):
	permission_classes = (permissions.AllowAny,)
	server_class = oauth2_settings.OAUTH2_SERVER_CLASS
	validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
	oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

	def post(self, request):
		username = request.POST.get('username')
		client_id = request.POST.get('client_id')
		grant_type = request.POST.get('grant_type')
		password = request.POST.get('password')
		user = None
		try:
			if username is None:
				raise User.DoesNotExist
			user = User.objects.get(pk=1)
			AccessToken.objects.filter(user = user, application=Application.objects.get(client_id=client_id)).delete()
		except Exception as e:
			return Response(e.message,status=400)

		url, headers, body, status = self.create_token_response(request)
		serializer = CUserSerializer(user)
		d = json.loads(body)
		req = { 'acces_data' : d, 'user' : serializer.data }
		return Response(req)