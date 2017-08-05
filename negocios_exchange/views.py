from negocios_exchange.models import Account_Type, Notification_Type, Notification, Country, Type_Token, Token_Verification, Wallet_Cashier, Bank_Type, Transaction_Confirm, User_Profile, Financial_Entity ,Transaction, Coin, Bank, Bank_Cashier, Type_Wallet, Wallet, Coin_Wallet, Transaction_Type,Transaction_Status,Transaction_Log
from django.contrib.auth.models import User, Group
from negocios_exchange.serializers import CUserRankingSerializer, Transaction_Status_IndicatorSerializer, Account_Type_Serializer, Notification_Serializer, CountrySerializer, WalletPublicSerializer, BankPublicSerializer, Transaction_StatusSerializer, CGroupSerializer,Bank_Type_Serializer, Financial_EntitySerializer, Transaction_ConfirmSerializer, Bank_CashierSerializer, TransactionSerializer, Transaction_TypeSerializer, User_ProfileSerializer, CUserSerializer, CGroupSerializer, Coin_Serializer, Type_Wallet_Serializer, BankSerializer, WalletSerializer
# from django.http import 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from django.http import HttpResponse, Http404
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from oauth2_provider.models import AccessToken, Application
from braces.views import CsrfExemptMixin
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.settings import oauth2_settings
from rest_framework import permissions
import json#, django_filters
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from datetime import datetime
from django.conf import settings
from django.template import loader
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from negocios_exchange import tasks
# from django_filters.rest_framework import DjangoFilterBackend
class Pagination(PageNumberPagination):
	page_size = 10
	def get_paginated_response(self, data):
		return Response({
			'links': {
			'next': self.get_next_link(),
			'previous': self.get_previous_link()
			},
			'total_pages': self.page.paginator.num_pages,
			'count': self.page.paginator.count,
			'results': data
		})

class UserListView(ListCreateAPIView):
	queryset = User.objects.filter(is_active = True)
	serializer_class = CUserSerializer
	def create(self, request):
		return insert_user(self, request, True)

class UserView(APIView):
	def get(self, request, pk=None, format=None):
		users = None
		if pk is not None: 
			users = get_object_or_404(User, pk=pk)
			serializer = CUserSerializer(users)
			return Response(serializer.data)
		return Response({'error' : 'server_error', 'message' : 'Id Invalido'}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, pk, format=None):
		print pk
		usr = get_object_or_404(User, pk=pk)
		serializer = CUserSerializer(usr, data=request.data, context={'request': request, 'wgroup': True} )
		if serializer.is_valid():
			serializer.save()	
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)	

	def delete(self, request, pk, format=None):
		try:
			usr = get_object_or_404(User, pk=pk)
			usr.is_active = False
			usr.save()
			usrr = get_object_or_404(User, pk=pk)
			usrr.is_active = False
			usrr.save()
			# if(usr.id == request.user.id)

			return Response(status=status.HTTP_204_NO_CONTENT)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 

def insert_user(self, request, flag):
	password = User.objects.make_random_password()
	import uuid
	uid = str(uuid.uuid1())
	serializer = CUserSerializer(data=request.data, context={'request': request, 'wgroup': flag, 'password': password, 'uid': uid} )
	if serializer.is_valid():
		serializer.save()	
		if serializer.data["group"]["id"] == 4:
			send_mail_user_signup(serializer.data, request.data["password"], uid)
		else:
			send_mail_user_signup(serializer.data, password, uid)
		return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)		

def send_mail_user_signup(data, password, uid):
	if(data["group"]["id"] != 4):
		msj_bienvenido = "Hola " + data["fullname"] + ", se le ha creado un perfil en Negocios Exchange. "
		msj_pass = "Password: " + Render_Bold(password)
	else:
		msj_bienvenido = "Hola " + data["fullname"] + ", su registro Negocios Exchange se ha realizado exitosamente"
		msj_pass = "Password: " + Render_Bold(password)

	msj_validacion = "Por favor, haga click en siguiente link para confirmar su email y activar su cuenta"
	msj_link = Render_Link("Confirmar Email", "http://localhost:3000/#!/activation/"+uid)	
	msj_usrname = "Nombre de Usuario: " + Render_Bold(data["username"]) 
	arr = [msj_bienvenido, msj_usrname, msj_pass, msj_validacion, msj_link]	
	return Render_Mail("Registro Negocios Exchange", data["email"], Render_Parrafos(arr))

class UserPublicViewSet(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request, format=None):
		return insert_user(self, request, False)

class Password_RecoveryViewSet(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request, format=None):
		if not "email" in request.data:
			err = "Debe Ingresar el Email"		
			return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST)
		user = get_object_or_404(User, email = request.data["email"])		
		try:		
			user.password = "";
			user.save()
			import uuid
			uid = str(uuid.uuid1())		
			tokv = Token_Verification(
				type_token = Type_Token(id = 2),
				user = user,
				token = uid,
				active = True
			)
			tokv.save()
			msj_1 = "Hola " + user.first_name + ","
			msj_2 = "Para esteblecer tu Password " + Render_Link("Ve a esta pagina", "http://localhost:3000/#!/reset/"+uid)
			arr = [msj_1,  msj_2]	
			Render_Mail("Recuperacion de Password", user.email, Render_Parrafos(arr))
			return Response({'succes' : True, 'message' : 'Recovery en Proceso'}, status= 200) 
		except Exception as e:
			return Response({'succes' : False, 'message' : 'Error de Servidor'}, status= 400) 

class  Password_ResetViewSet(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request, token=None, format=None):
		token = get_object_or_404(Token_Verification, token=token, active = True)
		try:		
			if not "password" in request.data:
				err = "Debe Ingresar el Password"	
				return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST) 
			user = token.user
			user.set_password(request.data["password"]);		
			user.save()	
			token.active = False
			token.save()
			msj_1 = "Hola " + user.first_name + ","
			msj_2 = "Tu Password en Negocios Exchange ha sido Restaurada Satisfactoriamente" 
			msj_3 = "Si no ha realizado esta accion, puede recuperar el acceso introduciendo " + Render_Link(user.email, user.email) + ", en el formulario " + Render_Link("http://iffdev.com/nexchange/#/reset/", "http://iffdev.com/nexchange/#/reset/")
			arr = [msj_1,  msj_2, msj_3]				
			Render_Mail("Recuperacion de Password", user.email, Render_Parrafos(arr))
			return Response({'succes' : True, 'message' : 'Password Restaurada Satisfactoriamente'}, status= 200) 
		except Exception as e:
			return Response({'succes' : False, 'message' : 'Error de Servidor'}, status= 400) 

class Verify_UserViewSet(APIView):
	permission_classes = (permissions.AllowAny,)
	def get(self, request, token=None, format=None):
		user = get_object_or_404(User_Profile, uid=token, deleted = False)
		try:
			if not user.verified:
				user.verified = True
				user.save()
				return Response({'verified' : True, 'message' : 'Usuario Verificado con Exito'}, status= 200) 
			else:
				return Response({'verified' : False, 'message' : 'El Usuario ya Fue Verificado'}, status= status.HTTP_403_FORBIDDEN) 
		except Exception as e:
			return Response({'error' : 'invalid_token', 'error_description' : 'Token de activacion no existe'}, status=401) 				

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
			upro = User_Profile.objects.filter(user__username = username)

			if len(upro) is 0:
				return Response({'success' : False, 'error' : 'invalid_credentials', 'error_description' : 'Credenciales Invalidas 2'}, status= 401) 

			if not upro[0].verified:
				return Response({'success' : False, 'error' : 'user_not_verified', 'error_description' : 'Usuario No Verificado'}, status= 403) 
			url, headers, body, status = self.create_token_response(request)
			d = json.loads(body)
			if not d.get("error"):
				serializer = CUserSerializer(upro[0].user)
				req = {'success' : True, 'acces_data' : d, 'user' : serializer.data }
				return Response(req)
			d["error_description"] = "Credenciales Invalidas 4"
			d["success"] = False
			return Response(d, status=401)			
		except Exception as e:
			# return e
			return Response({'error' : 'invalid_grant', 'error_description' : 'Credenciales Invalidas 3'}, status=401) 

class ProfileViewSet(APIView):
	def put(self, request, format=None):
		try:
			user = request.user
			user_prof = User_Profile.objects.get(user=user)
			if "password" in request.data:
				if request.data['password'] != None:
					user.set_password(request.data['password'])		
			if "fullname" in request.data:
				if request.data['fullname'] != None:
					user.first_name = request.data['fullname']
			if "phone_1" in request.data:
				if request.data['phone_1'] != None:
					user_prof.phone_1 = request.data['phone_1']
			if "phone_2" in request.data:
				if request.data['phone_2'] != None:
					user_prof.phone_2 = request.data['phone_2']
			if "birthdate" in request.data:
				if request.data['birthdate'] != None:
					user_prof.birthdate = request.data['birthdate']
			if "country" in request.data:
				if request.data['country'] != None:
					coun = get_object_or_404(Country, id = request.data['country'])
					user_prof.country = coun
			if "dni" in request.data:
				if request.data['dni'] != None:
					userdni = User_Profile.objects.filter(dni=request.data['dni']).exclude(user=user)
					if len(userdni) > 0: 
						return Response({'error' : 'server_error', 'message' :  'El Dni Ya Existe'}, status=status.HTTP_400_BAD_REQUEST)
					user_prof.dni = request.data['dni'] #

			user_prof.save()
			user.save()
			serializer = CUserSerializer(user, context={'request': request} )
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' :  'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST)

class CoinViewSet(ListAPIView):
	queryset = Coin.objects.all()
	serializer_class = Coin_Serializer

class Estatus_IndicatorViewSet(APIView):
	def get(self, request, format=None):
		con = Transaction_Status.objects.exclude(id= 1)
		serializer = Transaction_Status_IndicatorSerializer(con, context={'request': request}, many=True)
		return Response(serializer.data)

class RankingViewSet(APIView):
	def get(self, request, format=None):
		con = Transaction.objects.values('user').filter(transaction_status__id = 5).annotate(ucount=Count('id')).order_by('-ucount')[:10]
		us = list()
		for obj in con:
			u =  get_object_or_404(User, pk=obj["user"]) 
			serializer = CUserRankingSerializer(u, context={'quantity': obj["ucount"]})
			us.append(serializer.data) 
		return Response(us)		

class CountryViewSet(APIView):
	def get(self, request, format=None):
		con = Country.objects.all()
		serializer = CountrySerializer(con, many=True)
		return Response(serializer.data)	

class Type_WalletListViewSet(ListAPIView):
	queryset = Type_Wallet.objects.all()
	serializer_class = Type_Wallet_Serializer	

class Wallet_TypeUpViewSet(APIView):
	def put(self, request, pk, format=None):
		try:
			wt = get_object_or_404(Type_Wallet, pk=pk)
			if not "commission" in request.data:
				err = "Debe ingresar la comision"
				return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST)		
			wt.commission = request.data["commission"]
			wt.save()
			serializer = Type_Wallet_Serializer(wt)
			return Response(serializer.data, status=status.HTTP_200_OK)			
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Comision Invalida'}, status=status.HTTP_400_BAD_REQUEST)		

class Type_WalletViewSet(ListAPIView):
	queryset = Wallet.objects.all()
	serializer_class = WalletSerializer
	def list(self, request, *args, **kwargs):
		wallets = Wallet.objects.filter(deleted = False, type_wallet__id = kwargs['pk'])
		page = self.paginate_queryset(wallets)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(wallets, many=True)
		return Response(serializer.data)

class Financial_EntityViewSet(ListAPIView):
	queryset = Financial_Entity.objects.all()
	serializer_class = Financial_EntitySerializer

class GroupViewSet(ListAPIView):
	queryset = Group.objects.all()
	serializer_class = CGroupSerializer	

class CashiersViewSet(ListAPIView):
	queryset = User.objects.filter(groups__id=3)
	serializer_class = CUserSerializer	

class Bank_TypeListViewSet(ListAPIView):
	queryset = Bank_Type.objects.all()
	serializer_class = Bank_Type_Serializer	

class Bank_TypeUpViewSet(APIView):
	def put(self, request, pk, format=None):
		try:
			bt = get_object_or_404(Bank_Type, pk=pk)
			if not "commission" in request.data:
				err = "Debe ingresar la comision"
				return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST)		
			bt.commission = request.data["commission"]
			bt.save()
			serializer = Bank_Type_Serializer(bt)
			return Response(serializer.data, status=status.HTTP_200_OK)			
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Comision Invalida'}, status=status.HTTP_400_BAD_REQUEST) 		

class BankListViewSet(ListCreateAPIView):
	queryset = Bank.objects.all()
	serializer_class = BankSerializer
	def create(self, request):	
		serializer = BankSerializer(data=request.data, context={'request': request} )
		if serializer.is_valid():
			serializer.save()	
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)	

	def list(self, request, *args, **kwargs):
		if request.user.groups.filter(pk=4).exists():
			if "public" in request.GET:
				if request.GET["public"] == "1":
					banks = Bank.objects.filter(deleted = False, user = None, active = True)
				else:
					banks = Bank.objects.filter(deleted = False, user = request.user)
				page = self.paginate_queryset(banks)
				if page is not None:
					serializer = BankPublicSerializer(page, many=True)
					return self.get_paginated_response(serializer.data)

				serializer = BankPublicSerializer(banks, many=True)
				return Response(serializer.data)				
			else:
				banks = Bank.objects.filter(deleted = False, user = request.user)
		else:
			banks = Bank.objects.filter(deleted = False, user = None)

		page = self.paginate_queryset(banks)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(banks, many=True)
		return Response(serializer.data)

class BankViewSet(APIView):
	def get(self, request, pk=None, format=None):
		banks = get_object_or_404(Bank, pk=pk, deleted = False)
		serializer = BankSerializer(banks)
		return Response(serializer.data)	

	def put(self, request, pk, format=None):
		bank = get_object_or_404(Bank, pk=pk)
		serializer = BankSerializer(bank, data=request.data, context={'request': request} )
		if serializer.is_valid():
			serializer.save()	
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)			

	def delete(self, request, pk, format=None):
		try:
			bank = get_object_or_404(Bank, pk=pk)
			bank.deleted = True
			bank.save()
			return Response(status=status.HTTP_204_NO_CONTENT)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 

class WalletListViewSet(ListCreateAPIView):
	queryset = Wallet.objects.all()
	serializer_class = WalletSerializer
	def create(self, request):
		serializer = WalletSerializer(data=request.data, context={'request': request} )
		if serializer.is_valid():
			serializer.save()	
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)	

	def list(self, request, *args, **kwargs):
		if request.user.groups.filter(pk=4).exists():
			if "public" in request.GET:
				if request.GET["public"] == "1":
					wall = Wallet.objects.filter(deleted = False, user = None)
				else:
					wall = Wallet.objects.filter(user = request.user, deleted = False)

				page = self.paginate_queryset(wall)
				if page is not None:
					serializer = WalletPublicSerializer(page, many=True)
					return self.get_paginated_response(serializer.data)
				serializer = WalletPublicSerializer(wall, many=True)
				return Response(serializer.data)						
			else:
				wall = Wallet.objects.filter(user = request.user, deleted = False)
		else:
			wall = Wallet.objects.filter(deleted = False, user = None)

		page = self.paginate_queryset(wall)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		serializer = self.get_serializer(wall, many=True)
		return Response(serializer.data)				

class WalletViewSet(APIView):
	def get(self, request, pk=None, format=None):
		if request.user.groups.filter(pk=4).exists():
			wallet = get_object_or_404(Wallet, pk=pk, deleted = False, user = request.user)
		else:
			wallet = get_object_or_404(Wallet, pk=pk, deleted = False, user = None)
		serializer = WalletSerializer(wallet)
		return Response(serializer.data)

	def put(self, request, pk, format=None):
		wallet = get_object_or_404(Wallet, pk=pk)
		serializer = WalletSerializer(wallet, data=request.data, context={'request': request} )
		if serializer.is_valid():
			serializer.save()	
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)			

	def delete(self, request, pk, format=None):
		try:
			wallet = get_object_or_404(Wallet, pk=pk)
			wallet.deleted = True
			wallet.save()
			return Response(status=status.HTTP_204_NO_CONTENT)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 

class Transaction_TypeListViewSet(ListCreateAPIView):
	queryset = Transaction_Type.objects.all()
	serializer_class = Transaction_TypeSerializer

class Transaction_TypeViewSet(APIView):
	def get(self, request, pk=None, format=None):
		transaction_type = get_object_or_404(Transaction_Type, pk=pk, deleted = False)
		serializer = Transaction_TypeSerializer(transaction_type)
		if not "quantity" in request.GET:
			return Response(serializer.data)
		else:
			try:
				cant = float(request.GET["quantity"])
				quantity = cant / serializer.data["exchange_rate"]
				ef1_commission = 0
				ef2_commission = 0	
				if not "id_1" in request.GET:
					err = "Debe ingresar el id de la entidad 1 (id_1)"
					return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST)	

				if not "id_2" in request.GET:
					err = "Debe ingresar el id de la entidad 2 (id_2)"
					return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST)						

				if transaction_type.financial_entity_1.id == 1:
					bank_1 = get_object_or_404(Bank_Type, pk=request.GET["id_1"]) 
					ef1_commission = bank_1.commission
				else:			
					wallet_1 = get_object_or_404(Type_Wallet, pk=request.GET["id_1"]) 
					ef1_commission = wallet_1.commission
					
				if transaction_type.financial_entity_2.id == 1:
					bank_2 = get_object_or_404(Bank_Type, pk=request.GET["id_2"])		
					ef2_commission = bank_2.commission
				else:			
					wallet_2 = get_object_or_404(Type_Wallet, pk=request.GET["id_2"]) 
					ef2_commission = wallet_2.commission

				total_comi = ((transaction_type.transaction_commission + transaction_type.cashier_commission + ef1_commission + ef2_commission) *  quantity) / 100
				payment_total = quantity + total_comi
				return Response({'payment_total': round(payment_total, 2), 'exchange_total' : round(quantity, 2), 'exchange_transaction_commission' : round(total_comi, 2), 'exchange_quantity': round(cant, 2) }) 		
			except Exception, e:
				return Response({'error' : 'server_error', 'message' : 'Cantidad o Id de Entidad Invalido'}, status=status.HTTP_400_BAD_REQUEST) 		

	def put(self, request, pk, format=None):
		transaction_type = get_object_or_404(Transaction_Type, pk=pk)

		if not request.data.get('exchange_rate'):
			return Response({'exchange_rate': "Ingrese la Tarifa de Transaccion"}, status=status.HTTP_400_BAD_REQUEST) 

		if not request.data.get('transaction_commission'):
			return Response({'transaction_commission': "Ingrese la Cantidad de Comision de la Transaccion"}, status=status.HTTP_400_BAD_REQUEST) 

		if not request.data.get('cashier_commission'):
			return Response({'cashier_commission': "Ingrese la Comision del Cajero"}, status=status.HTTP_400_BAD_REQUEST) 

		try:
			transaction_type.exchange_rate = request.data.get('exchange_rate')
			transaction_type.transaction_commission = request.data.get('transaction_commission')
			transaction_type.cashier_commission = request.data.get('cashier_commission')
			transaction_type.save()
			serializer = Transaction_TypeSerializer(transaction_type,  context={'request': request} )
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception, e:
			return Response({'error' : 'corrupt_request', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 		

	def delete(self, request, pk, format=None):
		try:
			transaction_type = get_object_or_404(Transaction_Type, pk=pk)
			transaction_type.deleted = True
			transaction_type.save()
			return Response(status=status.HTTP_204_NO_CONTENT)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 

class TransactionListViewSet(ListCreateAPIView):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer

	def create(self, request):
		serializer = TransactionSerializer(data=request.data, context={'request': request} )
		if serializer.is_valid():
			serializer.save()	
			msj_1 = "Su transaccion se ha generado exitosamente:"
			msj_2 = Render_Bold("Codigo: ") + serializer.data["code"]
			msj_3 = Render_Bold("Cantidad Solicitada: ") + str(serializer.data["commission_detail"]["exchange_quantity"]) + " " + serializer.data["transaction_type"]["coin_2"]["code"]
			msj_4 = Render_Bold("Comision de Transaccion (" +str(serializer.data["transaction_type"]["transaction_commission"] + serializer.data["transaction_type"]["cashier_commission"] + serializer.data["ef1_commission"] + serializer.data["ef2_commission"])+"%): ") + str(serializer.data["commission_detail"]["exchange_transaction_commission"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
			msj_5 = Render_Bold("Total: ") + str(serializer.data["commission_detail"]["payment_total"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
			arr = [msj_1, msj_2, msj_3, msj_4, msj_5]	
			Render_Mail("Transaccion Generada", serializer.data["user"]["email"], Render_Parrafos(arr))			
			msj_6 = Render_Bold("Cliente: ") + str(serializer.data["user"]["fullname"]) 
			msj_7 = "Se ha creado una Nueva Transaccion:"
			if serializer.data["transaction_type"]["financial_entity_1"]["id"] == 1:
				for e in Bank_Cashier.objects.filter(bank__id = serializer.data["bank_1"]["id"]):
					arr = [msj_7, msj_2, msj_3, msj_4, msj_5, msj_6]	
					Render_Mail("Notificacion de Transaccion Generada", e.cashier.email, Render_Parrafos(arr))			
					Notificar_Transaccion(str(e.cashier.id), serializer.data, "Se ha creado una nueva transaccion") # NOTIFICACION
			else:
				for e in Wallet_Cashier.objects.filter(wallet__id = serializer.data["wallet_1"]["id"]):
					arr = [msj_7, msj_2, msj_3, msj_4, msj_5, msj_6]	
					Render_Mail("Notificacion de Transaccion Generada", e.cashier.email, Render_Parrafos(arr))						
					Notificar_Transaccion(str(e.cashier.id), serializer.data, "Se ha creado una nueva transaccion") # NOTIFICACION	
							
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)	
		
	def list(self, request, *args, **kwargs):
		if request.user.groups.filter(pk=3).exists():
			transactions = Transaction.objects.none()
			for e in Bank_Cashier.objects.filter(cashier = request.user):
				transactions = transactions | Transaction.objects.filter(bank_1__id = e.bank.id)
			for e in Wallet_Cashier.objects.filter(cashier = request.user):
				transactions = transactions | Transaction.objects.filter(wallet_1__id = e.wallet.id)
		elif request.user.groups.filter(Q(pk=1) | Q(pk=2)).exists():
			transactions = Transaction.objects.all()
		else:
			transactions = Transaction.objects.filter(user = request.user)
	# 		return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)

		if "from" in request.GET and "to" in request.GET:
			d1 = datetime.strptime(request.GET["from"], "%Y-%m-%d")
			d2 = datetime.strptime(request.GET["to"],  "%Y-%m-%d")
			d2 = d2.replace(hour=11, minute=59)
			transactions = transactions.filter(date__range=(d1, d2))	
		if "transaction_status" in request.GET:
			transactions = transactions.filter(transaction_status = request.GET["transaction_status"])	

		page = self.paginate_queryset(transactions.order_by('-date'))
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		serializer = self.get_serializer(transactions, many=True)
		return Response(serializer.data)

class TransactionViewSet(APIView):
	def get(self, request, pk=None, format=None):
		transaction = get_object_or_404(Transaction, pk=pk)
		serializer = TransactionSerializer(transaction)
		if request.user.groups.filter(pk=3).exists():
			if transaction.transaction_status.id == 1:
				if transaction.transaction_type.financial_entity_1.id == 1:
					ex_bank = Bank_Cashier.objects.filter(cashier = request.user, bank = transaction.bank_1)
					if len(ex_bank) > 0:
						return Response(serializer.data)
					else:
						return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN) 			
				else:
					ex_wallet = Wallet_Cashier.objects.filter(cashier = request.user, wallet = transaction.wallet_1)
					if len(ex_wallet) > 0:
						return Response(serializer.data)
					else:
						return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN) 							
			else:
				if transaction.cashier == request.user:
					return Response(serializer.data)	
				else:
					return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN) 			
		elif request.user.groups.filter(Q(pk=1) | Q(pk=2)).exists():
			return Response(serializer.data)
		else:
			return Response(serializer.data)
			# return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN) 	

class Transactions_CreatedViewSet(CreateAPIView):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer
	def create(self, request, *args, **kwargs):
		try:
			transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
			if transaction.transaction_status.id == 1: 
				status_t = Transaction_Status.objects.get(pk= 2)
				transaction.transaction_status = status_t
				transaction.cashier = request.user
				transaction.save()
				serializer = TransactionSerializer(transaction)
				msj_1 = "Su transaccion ya se encuentra en proceso:"
				msj_2 = Render_Bold("Codigo: ") + serializer.data["code"]
				msj_3 = Render_Bold("Cantidad Solicitada: ") + str(serializer.data["commission_detail"]["exchange_quantity"]) + " " + serializer.data["transaction_type"]["coin_2"]["code"]
				msj_4 = Render_Bold("Comision de Transaccion (" +str(serializer.data["transaction_type"]["transaction_commission"] + serializer.data["transaction_type"]["cashier_commission"] + serializer.data["ef1_commission"] + serializer.data["ef2_commission"])+"%):  ") + str(serializer.data["commission_detail"]["exchange_transaction_commission"])+ " " + serializer.data["transaction_type"]["coin_1"]["code"]
				msj_5 = Render_Bold("Total: ") + str(serializer.data["commission_detail"]["exchange_total"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
				msj_6 = Render_Bold("Operador: ") + str(serializer.data["cashier"]["fullname"])
				msj_7 = "Debe transferir el total a pagar a la cuenta:" 
				if serializer.data["transaction_type"]["financial_entity_1"]["id"] == 1:
					msj_8 = Render_Bold("Banco: ") + serializer.data["bank_1"]["bank"]["bank"]
					msj_9 = Render_Bold("Cta: ") + serializer.data["bank_1"]["account_type"]["type"]
					msj_10 = Render_Bold("Nro.: ") + serializer.data["bank_1"]["account"]
					msj_11 = Render_Bold("A nombre de: ") + serializer.data["bank_1"]["account_owner"]
					msj_12 = Render_Bold("Dni: ") + serializer.data["bank_1"]["account_dni"]
					msj_12 = Render_Bold("Email: ") + serializer.data["bank_1"]["account_email"]
					msj_13 = "Una vez que haga la transferencia, ingrese a la plataforma y registre su pago"
					arr = [msj_1, msj_2, msj_3, msj_4, msj_5, msj_6, msj_7, msj_8, msj_9, msj_10, msj_11, msj_12, msj_13]	
				else:
					msj_8 = serializer.data["wallet_1"]["type_wallet"]["type_wallet"]
					msj_9 = serializer.data["wallet_1"]["wallet"]
					msj_10 = "Una vez que haga la transferencia, ingrese a la plataforma y registre su pago"
					arr = [msj_1, msj_2, msj_3, msj_4, msj_5, msj_6, msj_7, msj_8, msj_9, msj_10]	
									
				Render_Mail("Transaccion en Proceso", serializer.data["user"]["email"], Render_Parrafos(arr))	
				msj_o_1 = "Ha tomado la transaccion " +Render_Bold(serializer.data["code"]) + " exitosamente"
				msj_o_2 = Render_Bold("Cliente: ") + str(serializer.data["user"]["fullname"])
				arr = [msj_o_1,  msj_3, msj_4, msj_5, msj_o_2]	

				Render_Mail("Transaccion en Proceso", serializer.data["cashier"]["email"], Render_Parrafos(arr))	
				Notificar_Transaccion(str(serializer.data["user"]["id"]), serializer.data, msj_1) # NOTIFICACION
				transaction_log = Transaction_Log(transaction = transaction, transaction_status = status_t, cashier = request.user, comment="System Log")
				transaction_log.save()
				# Notificar_Transaccion(str(transaction.user.id), serializer.data, False) # NOTIFICACION
					###### DEBO NOTIFICAR AL ADMINS ####
					###### DEBO MANDAR EL CORREO AL USUARIO, CAJERO Y ADMINS ####
				return Response(serializer.data, status=status.HTTP_200_OK)	
			else:
				return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)
		except Exception, e:
			return Response({'error' : e, 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST)

class Transactions_ConfirmViewSet(APIView):
	def post(self, request, pk=None, format=None):
		try:
			transaction = get_object_or_404(Transaction, pk=pk)
			serializer = TransactionSerializer(transaction)
			if request.user == transaction.user:
				if transaction.transaction_status.id == 2: 				
					status_t = Transaction_Status.objects.get(pk= 3)
					serializer_conf = Transaction_ConfirmSerializer(data=request.data, context={'flag': True, 'type': 'USUARIO', 'request': request, 'transaction': transaction} )
					if serializer_conf.is_valid():
						serializer_conf.save()	
						## MANDAR EMAIL AL USUARIO DE QUE CONFIRMO SATISFACTORIAMENTE ##
						msj_u_1 = "Se ha registrado su pago exitosamente"
						msj_u_2 = Render_Bold("Transaccion: ") + serializer.data["code"]
						msj_u_3 = Render_Bold("Cantidad Solicitada: ") + str(serializer.data["commission_detail"]["exchange_quantity"]) + " " + serializer.data["transaction_type"]["coin_2"]["code"]
						msj_u_4 = Render_Bold("Comision de Transaccion (" +str(serializer.data["transaction_type"]["transaction_commission"] + serializer.data["transaction_type"]["cashier_commission"] + serializer.data["ef1_commission"] + serializer.data["ef2_commission"])+"%): ") + str(serializer.data["commission_detail"]["exchange_transaction_commission"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
						msj_u_5 = Render_Bold("Total: ") + str(serializer.data["commission_detail"]["payment_total"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
						msj_u_6 = Render_Bold("Codigo de Confirmacion de Pago: ") + str(serializer_conf.data["code_confirmation"])
						arr = [msj_u_1, msj_u_2, msj_u_3, msj_u_4, msj_u_5, msj_u_6]	
						Render_Mail("Pago Registrado", serializer.data["user"]["email"], Render_Parrafos(arr))								
						## MANDAR EMAIL AL CAJERO DE QUE EL USUARIO CONFIRMO SU PAGO SATISFACTORIAMENTE ##
						msj_o_1 = "El cliente "+str(serializer.data["user"]["fullname"]) +" ha registrado un pago que debe verificar"
						arr = [msj_o_1, msj_u_2, msj_u_3, msj_u_4, msj_u_5, msj_u_6]	
						Render_Mail("Pago pendiente por verificar", serializer.data["cashier"]["email"], Render_Parrafos(arr))							
						## MANDAR NOTIFICACION AL CAJERO USUARIO DE QUE CONFIRMO SU PAGO SATISFACTORIAMENTE ##
						Notificar_Transaccion(str(serializer.data["cashier"]["id"]), serializer.data, msj_o_1) # NOTIFICACION

					else:
						return Response(serializer_conf.errors, status=status.HTTP_400_BAD_REQUEST)	
				elif transaction.transaction_status.id == 4: 
					## MANDAR EMAIL AL USUARIO DE QUE CONFIRMO QUE HA RECIBIDO EL PAGO Y LA TRANSACCION FINALIZO ##
					msj_u_1 = "Ha confirmado que el deposito de la transaccion " + Render_Bold(serializer.data["code"]) + " ha sido recibido exitosamente!"
					msj_u_2 = "Por lo tanto la transaccio ha sido finalizada"
					arr = [msj_u_1, msj_u_2]	
					Render_Mail("Transaccion Finalizada", serializer.data["user"]["email"], Render_Parrafos(arr))							
					## MANDAR EMAIL AL CAJERO DE QUE EL USUARIO CONFIRMO QUE HA RECIBIDO EL PAGO Y LA TRANSACCION FINALIZO ##
					msj_o_1 = "El cliente "+str(serializer.data["user"]["fullname"]) +" ha confirmado que el deposito de la transaccion " + Render_Bold(serializer.data["code"]) + " ha sido recibido exitosamente!"
					arr = [msj_o_1, msj_u_2]							
					Render_Mail("Transaccion Finalizada", serializer.data["cashier"]["email"], Render_Parrafos(arr))							
					## MANDAR NOTIFICACION AL CAJERO DE QUE EL USUARIO CONFIRMO QUE HA RECIBIDO EL PAGO Y LA TRANSACCION FINALIZO  ##					
					Notificar_Transaccion(str(serializer.data["cashier"]["id"]), serializer.data, msj_o_1) # NOTIFICACION
					status_t = Transaction_Status.objects.get(pk= 5)
				else:
					return Response({'error' : 'corrupt_request', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 
			elif request.user == transaction.cashier:
				if transaction.transaction_status.id == 3: 	
					serializer_conf = Transaction_ConfirmSerializer(data=request.data, context={'flag': False, 'type': 'CAJERO', 'request': request, 'transaction': transaction} )
					if serializer_conf.is_valid():
						serializer_conf.save()	
						## MANDAR EMAIL AL USUARIO DE QUE EL CAJERO LE HA TRANSFERIDO EL DINERO ##
						msj_u_1 = "Se le ha hecho un deposito que debe confirmar"
						msj_u_2 = Render_Bold("Transaccion: ") + serializer.data["code"]
						msj_u_3 = Render_Bold("Cantidad Solicitada: ") + str(serializer.data["commission_detail"]["exchange_quantity"]) + " " + serializer.data["transaction_type"]["coin_2"]["code"]
						msj_u_4 = Render_Bold("Comision de Transaccion (" +str(serializer.data["transaction_type"]["transaction_commission"] + serializer.data["transaction_type"]["cashier_commission"] + serializer.data["ef1_commission"] + serializer.data["ef2_commission"])+"%): ") + str(serializer.data["commission_detail"]["exchange_transaction_commission"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
						msj_u_5 = Render_Bold("Total: ") + str(serializer.data["commission_detail"]["payment_total"]) + " " + serializer.data["transaction_type"]["coin_1"]["code"]
						msj_u_6 = Render_Bold("Codigo de Confirmacion de Deposito: ") + str(serializer_conf.data["code_confirmation"])
						arr = [msj_u_1, msj_u_2, msj_u_3, msj_u_4, msj_u_5, msj_u_6]	
						Render_Mail("Deposito Recibido", serializer.data["user"]["email"], Render_Parrafos(arr))					
						## MANDAR EMAIL AL CAJERO DE QUELE HA TRANSFERIDO EL DINERO AL USUARIO SATISFACTORIAMENTE##
						msj_o_1 = "Se ha registrado el pago al cliente "+str(serializer.data["user"]["fullname"]) + " exitosamente"
						arr = [msj_o_1, msj_u_2, msj_u_3, msj_u_4, msj_u_5, msj_u_6]	
						Render_Mail("Pago pendiente por verificar", serializer.data["cashier"]["email"], Render_Parrafos(arr))						
						## MANDAR NOTIFICACION AL USUARIO DE QUE EL CAJERO LE HA TRANSFERIDO EL DINERO  ##										
						Notificar_Transaccion(str(serializer.data["user"]["id"]), serializer.data, msj_u_1) # NOTIFICACION						
					else:
						return Response(serializer_conf.errors, status=status.HTTP_400_BAD_REQUEST)										
					status_t = Transaction_Status.objects.get(pk= 4)
				else:
					return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)
			else:
				return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN) 
			transaction.transaction_status = status_t
			transaction.save()		
			transaction_log = Transaction_Log(transaction = transaction, transaction_status = status_t, cashier = request.user, comment="System Log")
			transaction_log.save()	
			return Response(serializer.data, status=status.HTTP_200_OK)	
		except Exception, e:
			return Response({'error' : 'server_error', 'message' : 'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST) 

class Transactions_Active(APIView):
	def get(self, request, format=None):
		if request.user.groups.filter(pk=4).exists():
			exist_transaction = Transaction.objects.filter(user = request.user).exclude(transaction_status__id__in = [5,6])
			if len(exist_transaction) > 0:			
				return Response({'active' : 1}, status=status.HTTP_200_OK)
			return Response({'active' : 0}, status=status.HTTP_200_OK)
		return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)

class Transactions_RejectViewSet(CreateAPIView):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer
	def create(self, request, *args, **kwargs):
		try:
			transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
			if request.user.groups.filter(Q(pk=1) | Q(pk=2)).exists():
				if transaction.transaction_status.id != 5 and transaction.transaction_status.id != 6:
					msg = "Sin Observacion"
					if 'comment' in request.data:
						msg = request.data["comment"]
					status_t = Transaction_Status.objects.get(pk= 6)
					transaction.transaction_status = status_t
					transaction.save()
					transaction_log = Transaction_Log(transaction = transaction, transaction_status = status_t, cashier = request.user, comment=msg)
					transaction_log.save()	
					serializer = TransactionSerializer(transaction)		
					msj_u_1 = "La transaccion " + Render_Bold(serializer.data["code"]) + " ha sido rechazada"
					msj_u_2 = Render_Bold("Observacion: ") + msg
					arr = [msj_u_1, msj_u_2]	
					Render_Mail("Transaccion Rechazada", serializer.data["user"]["email"], Render_Parrafos(arr))	
					Notificar_Transaccion(str(serializer.data["user"]["id"]), serializer.data, msj_u_1) # NOTIFICACION						
					if serializer.data["cashier"] != None:			
						Render_Mail("Transaccion Rechazada", serializer.data["cashier"]["email"], Render_Parrafos(arr))		
						Notificar_Transaccion(str(serializer.data["cashier"]["id"]), serializer.data, msj_u_1) # NOTIFICACION						

					return Response(serializer.data, status=status.HTTP_200_OK)	
				else:
					return Response({'error' : 'acces_denied', 'message' : 'La Transaccion ya ha Finalizada o Desestimada'}, status=status.HTTP_403_FORBIDDEN)
			else:
				return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' :  'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST)

class Transactions_DisputeViewSet(CreateAPIView):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer
	def create(self, request, *args, **kwargs):
		try:
			transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
			if transaction.user == request.user or request.user.groups.filter(Q(pk=1) | Q(pk=2)).exists():
				if transaction.transaction_status.id != 5 and transaction.transaction_status.id != 6:
					msg = "Sin Observacion"
					if 'comment' in request.data:
						msg = request.data["comment"]					
					status_t = Transaction_Status.objects.get(pk= 7)
					transaction.transaction_status = status_t
					transaction.save()
					transaction_log = Transaction_Log(transaction = transaction, transaction_status = status_t, cashier = request.user, comment=msg)
					transaction_log.save()	
					serializer = TransactionSerializer(transaction)		
					msj_u_1 = "La transaccion " + Render_Bold(serializer.data["code"]) + " ha sido puesta en el estatus de Disputa"
					msj_u_2 = Render_Bold("Observacion: ") + msg
					arr = [msj_u_1, msj_u_2]	
					Render_Mail("Transaccion en Disputa", serializer.data["user"]["email"], Render_Parrafos(arr))	
					Notificar_Transaccion(str(serializer.data["user"]["id"]), serializer.data, msj_u_1) # NOTIFICACION						
					if serializer.data["cashier"] != None:			
						Render_Mail("Transaccion en Disputa", serializer.data["cashier"]["email"], Render_Parrafos(arr))		
						Notificar_Transaccion(str(serializer.data["cashier"]["id"]), serializer.data, msj_u_1) # NOTIFICACION						
					return Response(serializer.data, status=status.HTTP_200_OK)	
				else:
					return Response({'error' : 'acces_denied', 'message' : 'La Transaccion ya ha Finalizada o Desestimada'}, status=status.HTTP_403_FORBIDDEN)
			else:
				return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' :  'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST)			

class EstatusViewSet(ListAPIView):
	queryset = Transaction_Status.objects.exclude(pk=1).exclude(pk=2).exclude(pk=7)
	serializer_class = Transaction_StatusSerializer

class Account_TypeViewSet(ListAPIView):
	queryset = Account_Type.objects.all()
	serializer_class = Account_Type_Serializer	

class NotificationVierSet(ListCreateAPIView):
	queryset = Notification.objects.all()
	serializer_class = Notification_Serializer	
	def create(self, request, *args, **kwargs):
		noti = get_object_or_404(Notification, pk=kwargs['pk'])	
		if request.user == noti.user:
			noti.viewed = True
			noti.save()
			serializer = Notification_Serializer(noti)		
			return Response(serializer.data, status=status.HTTP_200_OK)	
		return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)

	def list(self, request, *args, **kwargs):
		nois = Notification.objects.filter(user=request.user).order_by('-date')
		page = self.paginate_queryset(nois)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)			
		serializer = self.get_serializer(page, many=True)
		return self.get_paginated_response(serializer.data)

class Transactions_Change_StatusViewSet(CreateAPIView):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer
	def create(self, request, *args, **kwargs):
		try:
			transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
			if request.user.groups.filter(Q(pk=1) | Q(pk=2)).exists():
				if kwargs['st'] == "1" or kwargs['st'] == "2" or kwargs['st'] == "7":
					err = "Estatus Invalido"
					return Response({'message': err}, status=status.HTTP_400_BAD_REQUEST)					

				status_t = Transaction_Status.objects.get(pk= kwargs['st'])
				transaction.transaction_status = status_t
				transaction.save()
				transaction_log = Transaction_Log(transaction = transaction, transaction_status = status_t, cashier = request.user, comment="System Log")
				transaction_log.save()	
				serializer = TransactionSerializer(transaction)		
				return Response(serializer.data, status=status.HTTP_200_OK)	
			else:
				return Response({'error' : 'acces_denied', 'message' : 'Acceso Denegado'}, status=status.HTTP_403_FORBIDDEN)
		except Exception, e:
			return Response({'error' : 'server_error', 'message' :  'Error de Servidor'}, status=status.HTTP_400_BAD_REQUEST)

class PushView(APIView):
	def post(self, request):
		transaction = get_object_or_404(Transaction, pk=28)
		serializer = TransactionSerializer(transaction)
		ss = Notificar_Transaccion(str(request.user.id), serializer.data, "Se ha creado una nueva transaccion")
		return Response({"message" : 'ss'}, status=status.HTTP_200_OK)

def Notificar_Transaccion(canal, transacccion, flag):
	notif = Notification(
		transaction = Transaction(id= transacccion["id"]),
		user = User.objects.get(pk = canal),
		type = Notification_Type.objects.get(pk = 1),
		title = flag
	)
	notif.save()	
	seri_noti = Notification_Serializer(Notification.objects.get(pk = notif.id)).data
	_id_ = str(transacccion["id"])
	_code_ = transacccion["code"]
	_cashier_ = ('null' if transacccion["cashier"] == None  else '{"fullname":"'+transacccion["cashier"]["fullname"]+'", "id": '+str(transacccion["cashier"]["id"])+', "email":"'+transacccion["cashier"]["email"]+'"}')
	_transaction_type_ = '{"id":'+str(transacccion["transaction_type"]["id"])+',"transaction_type": "'+transacccion["transaction_type"]["transaction_type"]+'", "coin_1":{"coin":"'+transacccion["transaction_type"]["coin_1"]["coin"]+'", "id":'+str(transacccion["transaction_type"]["coin_1"]["id"])+'}, "coin_2":{"coin":"'+transacccion["transaction_type"]["coin_2"]["coin"]+'", "id":'+str(transacccion["transaction_type"]["coin_2"]["id"])+'}}'
	_quantity_ = str(transacccion["quantity"])
	_date_ = transacccion["date"]
	_transaction_status_ = '{"id":'+str(transacccion["transaction_status"]["id"])+', "transaction_status":"'+transacccion["transaction_status"]["transaction_status"]+'"}'
	_user_ = '{"fullname":"'+transacccion["user"]["fullname"]+'", "id": '+str(transacccion["user"]["id"])+', "email":"'+transacccion["user"]["email"]+'"}'
	transacccion = '{"id":'+_id_+',"code":"'+_code_+'", "cashier":'+_cashier_+',"transaction_type":'+_transaction_type_ +',"quantity":'+_quantity_+',"date":"'+_date_+'","transaction_status":'+_transaction_status_+', "user": ' + _user_ + '}'
	_user_noti_ = '{"fullname":"'+seri_noti["user"]["fullname"]+'", "id": '+str(seri_noti["user"]["id"])+', "email":"'+seri_noti["user"]["email"]+'"}'
	_type_ = '{"id" : '+str(notif.type.id)+', "type" : "'+str(notif.type.type)+'"}'
	_date_noti_ = seri_noti["date"]
	_viewed_ = str(notif.viewed).lower() 
	_id_noti_ = str(notif.id)
	obj = '{"title": "'+ flag +'", "id":'+_id_noti_+', "transaction": '+ transacccion +', "user":'+_user_noti_+', "date": "'+_date_noti_+'", "viewed": '+_viewed_+', "type": '+_type_+' }'
	Notificar(canal, obj)
	# obj = '{"title": ""}'
	return obj

def Notificar(canal_name, msj):
	from ably import AblyRest
	cliente = AblyRest("IdGeHg.HinOhw:M13HoeLS7pcwjQdz")
	canal = cliente.channels.get(canal_name)
	canal.publish(canal_name, msj)

def Render_Bold(Text):
	return "<b>"+Text+"</b>"

def Render_Link(Text, Url):
	return '<a href="'+Url+'" style="color:#ff006f;text-decoration:underline" target="_blank">'+Text+'</a>'

def Render_Parrafos(parrafos):
	html = ""
	for obj in parrafos:
		html += ' <p class="m_-6520767629608970887intercom-align-left" style="color:#162e34;font-size:16px;line-height:1.5;margin:0 0 25px;text-align:left!important" align="left">'+obj+'</p>'
	return html

def Render_Mail(Subject, To, Body, From = "Negocios Exchange info@negociosexchange.com", Cc=""):
	# import smtplib
	# from email.mime.multipart import MIMEMultipart
	# from email.mime.text import MIMEText
	Url_Sistema = "#"
	html = '<html lang="es-ES"><head><meta charset="utf-8"></head><body><div style="background:#f0f0f0;margin:0;padding:10px 0" bgcolor="#f0f0f0"><br><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" bgcolor="#f0f0f0"><tbody><tr><td align="center" valign="top" bgcolor="#f0f0f0" style="background:#f0f0f0"><table width="600" cellpadding="0" cellspacing="0" border="0" class="m_-6520767629608970887container" bgcolor="#ffffff" style="border-bottom-color:#e0e0e0;border-bottom-style:solid;border-bottom-width:1px;color:#162e34;font-family:Helvetica,Verdana,sans-serif"><tbody><tr><td class="m_-6520767629608970887header" style="border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px"><div style="background:#162e34;border:1px solid #162e34;border-radius:2px;height:5px">&nbsp;</div></td></tr><tr><td class="m_-6520767629608970887logo" style="border-bottom-color:#efefef;border-bottom-style:solid;border-bottom-width:1px;border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px;padding:15px 0;text-align:center" align="center"><img src="http://iffdev.com/nexchange/assets/img/nexchange.png" width="238" height="180" alt="" class="CToWUd"></td></tr><tr><td class="m_-6520767629608970887container-padding" bgcolor="#ffffff" style="background:#ffffff;border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px;padding-left:30px;padding-right:30px"><br>'+	Body+'</td></tr><tr><td style="border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px"><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" bgcolor="#fbfbfb" class="m_-6520767629608970887footer" style="border-top-color:#efefef;border-top-style:solid;border-top-width:1px;height:69px;width:100%"><tbody><tr> <td class="m_-6520767629608970887social" style="border-left-color:#e0e0e0;border-left-style:none;border-left-width:1px;color:#434343;font-size:12px;line-height:20px;text-align:center;vertical-align:middle;width:60%" align="center" valign="middle">Ingresar Al Sistema: &nbsp; <a href="'+Url_Sistema+'"> Sistema</a> &nbsp;</td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table><br></div></body></html>'
	# msg = MIMEMultipart('alternative') 
	# msg['Subject'] = Subject
	# msg['From']    = From
	# msg['To']      = To
	# part_html = MIMEText(html, 'html')
	# msg.attach(part_html)
	# s = smtplib.SMTP('smtp.mailgun.org', 587)
	# s.login('postmaster@sistema-ac.com', 'f2ecc9972d233e470d3a959097fca3e7')
	# s.sendmail(msg['From'], msg['To'], msg.as_string())
	# s.quit()
	import requests
	# from requests.packages.urllib3.exceptions import InsecureRequestWarning, InsecurePlatformWarning
	# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	# requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
	requests.post(	
	 "https://api.mailgun.net/v3/sistema-ac.com/messages",
	 verify=False,
	 auth=("api", "key-83bba8a17bf83f1f4f2582cd7dfb1c8e"),
	 data={"from": From,
	       "to": [To],
	       "subject": Subject,
	       "html": html})


class EmailView(APIView):
	def post(self, request):
		Parrafos = ["Este es un parrafo Normal", "Prueba Normal " +Render_Bold("Este es un parrafo en negrita"), "Este es un parrafo con " + Render_Link("Link","www.mipagina.com")];
		# tasks.Render_Mail.delay("Test Subject", "luis.roberto.silva.guillen@gmail.com", Render_Parrafos(Parrafos))
		Render_Mail("Test Subject", "luis.roberto.silva.guillen@gmail.com", Render_Parrafos(Parrafos))
		return Response({"message" : "Ya"}, status=status.HTTP_200_OK)

