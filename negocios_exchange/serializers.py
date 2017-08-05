from rest_framework import serializers, pagination
from negocios_exchange.models import Account_Type, Notification_Type, Notification, Country, Transaction, Bank_Type, Wallet_Cashier, Transaction_Confirm, Financial_Entity, Transaction_Status, Transaction_Log,Transaction_Type,  User_Profile, Token_Verification, Type_Token, Coin, Bank, Bank_Cashier, Type_Wallet, Wallet, Coin_Wallet
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
import uuid 
from django.db.models import Q

class CUserRankingSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	quantity = serializers.SerializerMethodField()
	class Meta:
		model = User
		fields = ('user', 'quantity')
		write_only_fields = ()
		read_only_fields = ()	

	def get_user(self, obj):
		return {"id": obj.id, "username": obj.username, "email": obj.email, "fullname": obj.first_name}

	def get_quantity(self, obj):
		return self.context["quantity"]				

class CUserSerializer(serializers.ModelSerializer):
	dni = serializers.SerializerMethodField()
	phone_1 = serializers.SerializerMethodField()
	fullname = serializers.SerializerMethodField()
	phone_2 = serializers.SerializerMethodField()
	group = serializers.SerializerMethodField()
	birthdate = serializers.SerializerMethodField()
	country = serializers.SerializerMethodField()
	class Meta:
		model = User
		# fields = ('id', 'username', 'first_name', 'last_name', 'email','profile','group')
		fields = ('id', 'username',  'fullname', 'email','group', 'dni', 'phone_1','phone_2','birthdate','country')
		write_only_fields = ('password', 'first_name', 'last_name')
		read_only_fields = ('is_active', 'date_joined',)

	def create(self, validated_data):
		user = User(
			email=self.context["request"].data['email'],
			first_name=self.context["request"].data['fullname'],
			# last_name=validated_data['last_name'],
			username=self.context["request"].data['username'],
		)	
		user.set_password(self.context["password"]);		
		user.save()	
		if self.context["wgroup"]:
			grp = Group.objects.get(pk=self.context["request"].data['group'])
						
			uprofile = User_Profile(
				user = user,
				uid = self.context['uid']
			)		
		else:
			grp = Group.objects.get(pk = 4)
			user.set_password(self.context["request"].data['password']);
			user.save()	
			phone_2 = ""
			dni = ""
			if 'phone_2' in self.context["request"].data:
				phone_2 = self.context["request"].data.get('phone_2')

			if 'dni' in self.context["request"].data:
				dni = self.context["request"].data.get('dni')				

			uprofile = User_Profile(
				user = user,
				dni = dni,
				phone_1 = self.context["request"].data.get('phone_1'),
				phone_2 =	phone_2,
				uid = self.context['uid']
			)
			

		uprofile.save()
		grp.user_set.add(user.id)		
		return user

	def update(self, instance, validated_data):
		instance.first_name = self.context["request"].data.get('fullname', instance.first_name)
		# instance.last_name = validated_data.get('last_name', instance.first_name)
		instance.email = self.context["request"].data.get('email', instance.email)
		instance.is_active = self.context["request"].data.get('is_active', instance.is_active)
		instance.save()
		if self.context["wgroup"]:
			# Group.objects.get(pk=self.context["request"].data['group']).delete()
			instance.groups.clear()
			grp = Group.objects.get(pk=self.context["request"].data['group'])
			# grp.user_set.remove(instance)
			grp.user_set.add(instance.id)	
		return instance

	def validate(self, data):
		if not data.get('username'):
			raise serializers.ValidationError("Ingrese el Usuario")	

		if not self.context["request"].data.get('fullname'):
			raise serializers.ValidationError("Ingrese el Nombre")
			
		if not self.context["request"].data.get('email'):
			raise serializers.ValidationError("Ingrese el Email")	



		if self.context["wgroup"]:
			if not self.context["request"].data.get('group'):
				raise serializers.ValidationError("Seleccione el Grupo")	
			else:
				try:
					grp = Group.objects.get(pk=self.context["request"].data['group'])	
				except Exception, e:
					raise serializers.ValidationError("Grupo Invalido")	
		else:
			if not self.context["request"].data.get('password'):
				raise serializers.ValidationError("Ingrese el Password")

			if not self.context["request"].data.get('phone_1'):
				raise serializers.ValidationError("Ingrese el Telefono 1")	

			if not self.context["request"].data.get('dni'):
				raise serializers.ValidationError("Ingrese el Dni")						


		if self.context["request"].method == "POST":
			useremail = User.objects.filter(email=self.context["request"].data.get('email'))
			if len(useremail) > 0: 
				raise serializers.ValidationError("El Email Ya Existe")		

		return data
			# if self.context["request"].data.get('dni'):
			# 	userdni = User_Profile.objects.filter(dni=self.context["request"].data.get('dni'))
			# 	if len(userdni) > 0: 
			# 		raise serializers.ValidationError("El Dni Ya Existe")	

	def get_fullname(self, obj):
		return obj.first_name

	def get_birthdate(self, obj):
		try:
			user_prof = User_Profile.objects.get(user=obj)
			if user_prof != None:
				return user_prof.birthdate
		except Exception, e:
			return None

	def get_country(self, obj):
		try:
			user_prof = User_Profile.objects.get(user=obj)
			if user_prof != None and user_prof.country != None:
				return CountrySerializer(user_prof.country).data 
		except Exception, e:
			return None
		return None

	def get_dni(self, obj):
		try:
			user_prof = User_Profile.objects.get(user=obj)
			if user_prof != None:
				return user_prof.dni
		except Exception, e:
			return None

	def get_phone_1(self, obj):
		try:
			user_prof = User_Profile.objects.get(user=obj)
			if user_prof != None:
				return user_prof.phone_1 
		except Exception, e:
			return None		

	def get_phone_2(self, obj):
		try:
			user_prof = User_Profile.objects.get(user=obj)
			if user_prof != None:
				return user_prof.phone_2 
		except Exception, e:
			return None			

	def get_group(self, obj):
		try:
			group = obj.groups.all()
			if len(group):
				return CGroupSerializer(group[0]).data
		except Exception, e:
			return None

def EsEntero(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

class CGroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ('id', 'name')
		write_only_fields = ('id', )
		read_only_fields = ()        

class CountrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Country
		fields = ('id', 'name')
		write_only_fields = ()
		read_only_fields = ()      		

class User_ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User_Profile
		fields = ('id', 'verified')
		write_only_fields = ()
		read_only_fields = ()        

class Coin_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Coin
		fields = ('id', 'coin','code')
		write_only_fields = ()
		read_only_fields = ('code')    

class Type_Wallet_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Type_Wallet
		fields = ('id', 'code', 'type_wallet', 'commission')
		write_only_fields = ('url_icon')
		read_only_fields = ()    

	# def update(self, instance, validated_data):
	# 	instance.commission = self.context["request"].data.get('commission')
	# 	instance.save()

	# def validate(self, data):		
	# 	if self.context["request"].method == "PUT":		
	# 		if not self.context["request"].data.get('commission'):
	# 			raise serializers.ValidationError("Ingrese la comision")		
		# return data

class Bank_CashierSerializer(serializers.ModelSerializer):
	cashier = serializers.SerializerMethodField()
	class Meta:
		model = Bank_Cashier
		fields = ('cashier',)
		write_only_fields = ('bank')
		read_only_fields = ()    
	def get_cashier(self, obj):
		return CUserSerializer(obj.cashier).data

class Bank_Type_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Bank_Type
		fields = ('id', 'bank', 'commission',)
		write_only_fields = ()
		read_only_fields = ()   

	# def update(self, instance, validated_data):
	# 	instance.commission = self.context["request"].data.get('commission')
	# 	instance.save()

	# def validate(self, data):		
	# 	if self.context["request"].method == "PUT":		
	# 		if not self.context["request"].data.get('commission'):
	# 			raise serializers.ValidationError("Ingrese la comision")	
	# 	return data

class Account_Type_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Account_Type
		fields = ('id', 'type')
		write_only_fields = ()
		read_only_fields = ()  		

class BankPublicSerializer(serializers.ModelSerializer):
	type = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	id_type = serializers.SerializerMethodField()
	class Meta:
		model = Bank
		fields = ('id', 'type', 'name', 'id_type')
		write_only_fields = ()
		read_only_fields = ()    		

	def get_id_type(self, obj):
		return obj.bank.id

	def get_type(self, obj):
		return obj.bank.bank

	def get_name(self, obj):
		return obj.account		

class BankSerializer(serializers.ModelSerializer):
	cashiers = serializers.SerializerMethodField()
	bank = serializers.SerializerMethodField()
	account_type = serializers.SerializerMethodField()
	class Meta:
		model = Bank
		fields = ('id', 'bank', 'active', 'account', 'balance', 'cashiers', 'account_owner','account_dni', 'account_email','account_type')
		write_only_fields = ('deleted', 'user')
		read_only_fields = ()    			

	def create(self, validated_data):
		bnk = Bank_Type.objects.get(pk=self.context["request"].data.get('bank'))
		bank = Bank(
			bank = bnk,
			account =  self.context["request"].data.get('account'),
		)
		if self.context["request"].user.groups.filter(Q(pk=4)).exists():
			bank.user = self.context["request"].user
		else:
			bank.balance = self.context["request"].data.get('balance') 

		bank.account_owner = self.context["request"].data.get('account_owner')
		bank.account_dni = self.context["request"].data.get('account_dni')
		bank.account_email = self.context["request"].data.get('account_email')
		bank.account_type = Account_Type(id = self.context["request"].data.get('account_type')) 
		bank.save()

		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():
			bank_chashiers = self.context["request"].data.getlist('cashiers[]')
			for obj in bank_chashiers:
				user = User.objects.get(pk=obj)
				bank_cashier = Bank_Cashier(
					bank = bank,
					cashier = user
				)
				bank_cashier.save()
		return bank

	def update(self, instance, validated_data):
		instance.bank = Bank_Type.objects.get(pk=self.context["request"].data.get('bank'))
		instance.account = validated_data.get('account', instance.account)
		instance.active = validated_data.get('active', instance.active)
		instance.account_owner = self.context["request"].data.get('account_owner')
		instance.account_dni = self.context["request"].data.get('account_dni')
		instance.account_email = self.context["request"].data.get('account_email')
		instance.account_type = Account_Type.objects.get(pk=self.context["request"].data.get('account_type'))
		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():
			instance.balance = validated_data.get('balance', instance.balance)

		instance.save()
		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():
			chashiersD = Bank_Cashier.objects.filter(bank=instance.id).delete()
			bank_chashiers = self.context["request"].data.getlist('cashiers[]')
			for obj in bank_chashiers:
				user = User.objects.get(pk=obj)
				bank_cashier = Bank_Cashier(
					bank = instance,
					cashier = user
				)
				bank_cashier.save()		
		return instance

	def validate(self, data):			
		if not self.context["request"].data.get('bank'):
			raise serializers.ValidationError("Seleccione el Banco")
		else:
			try:
				bnk = Bank_Type.objects.get(pk=self.context["request"].data.get('bank'))
			except Exception, e:
				raise serializers.ValidationError("Banco Invalido" )			

		if not self.context["request"].data.get('account_owner'):
			raise serializers.ValidationError("Ingrese el Nombre del Propietario de la Cuenta")	

		if not self.context["request"].data.get('account_dni'):
			raise serializers.ValidationError("Ingrese el Dni del Propietario de la Cuenta")

		if not self.context["request"].data.get('account_email'):
			raise serializers.ValidationError("Ingrese el Email del Propietario de la Cuenta")	

		if not self.context["request"].data.get('account_type'):
			raise serializers.ValidationError("Ingrese el Tipo de Cuenta")	
		else:	
			try:
				account_type = Account_Type.objects.get(pk=self.context["request"].data.get('account_type'))
			except Exception, e:
				raise serializers.ValidationError("Tipo de Cuenta Invalido")							

		if not self.context["request"].data.get('account'):
			raise serializers.ValidationError("Ingrese el Numero de Cuenta")

		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():
			if self.context["request"].method == "POST":
				if not data.get('balance'):
					raise serializers.ValidationError("must_enter_the_balance")			

			if self.context["request"].method == "PUT":
				if not "active" in data:
					raise serializers.ValidationError("Ingrese el Estatus")						

			# print self.context["request"].data.getlist('cashiers[]')
			if not self.context["request"].data.getlist('cashiers[]'):			
				raise serializers.ValidationError("Seleccione el/los Cajero(s) del Banco")		

			bank_chashiers = self.context["request"].data.getlist('cashiers[]')
			for obj in bank_chashiers:
				try:
					user = User.objects.get(pk=obj)
				except Exception, e:
					raise serializers.ValidationError("Cajero Invalido")	

				if not user.groups.filter(pk=3).exists():
					raise serializers.ValidationError("El Usuario "+ user.first_name + " no es un Cajero")				
		
		return data

	def get_cashiers(self, obj):
		cashiers = Bank_Cashier.objects.filter(bank = obj)
		if len(cashiers):
			us = list()
			for obj in cashiers:
				us.append(obj.cashier) 
			return CUserSerializer(us, many=True).data
		return None

	def get_account_type(self, obj):
		return Account_Type_Serializer(obj.account_type).data

	def get_bank(self, obj):
		return Bank_Type_Serializer(obj.bank).data

class Wallet_CashierSerializer(serializers.ModelSerializer):
	cashier = serializers.SerializerMethodField()
	class Meta:
		model = Wallet_Cashier
		fields = ('cashier',)
		write_only_fields = ('wallet')
		read_only_fields = ()    
	def get_cashier(self, obj):
		return CUserSerializer(obj.cashier).data

class WalletPublicSerializer(serializers.ModelSerializer):
	type = serializers.SerializerMethodField()
	id_type = serializers.SerializerMethodField()
	name = serializers.SerializerMethodField()
	class Meta:
		model = Wallet
		fields = ('id', 'type', 'name', 'id_type')
		write_only_fields = ()
		read_only_fields = ()    		

	def get_type(self, obj):
		return obj.type_wallet.type_wallet

	def get_id_type(self, obj):
		return obj.type_wallet.id		
		
	def get_name(self, obj):
		return obj.wallet	

class WalletSerializer(serializers.ModelSerializer):
	type_wallet = serializers.SerializerMethodField()
	cashiers = serializers.SerializerMethodField()
	user = serializers.SerializerMethodField()
	class Meta:
		model = Wallet
		fields = ('id', 'wallet', 'active', 'type_wallet', 'balance', 'cashiers', 'user')
		write_only_fields = ()
		read_only_fields = ()    		

	def validate(self, data):			
		if not data.get('wallet'):
			raise serializers.ValidationError("Ingrese la Billetera")	

		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():
			if not self.context["request"].data.getlist('cashiers[]'):			
				raise serializers.ValidationError("Seleccione el/los Cajero(s) de la Billetera")		

			wallet_chashiers = self.context["request"].data.getlist('cashiers[]')
			for obj in wallet_chashiers:
				try:
					user = User.objects.get(pk=obj)
				except Exception, e:
					raise serializers.ValidationError("Cajero Invalido")	

				if not user.groups.filter(pk=3).exists():
					raise serializers.ValidationError("El Usuario "+ user.first_name + " no es un Cajero")		

			if self.context["request"].method == "POST":
				if not 'balance' in data:
					raise serializers.ValidationError("Ingrese el Saldo de la Billetera")							
		# else:
		# 	raise serializers.ValidationError("No tiene permiso para esta accion")		


		if self.context["request"].method == "PUT":
			if not "active" in data:
				raise serializers.ValidationError("Ingrese el Estatus de la Billetera")		

		if not self.context["request"].data.get('type_wallet'):
			raise serializers.ValidationError("Seleccione el Tipo de Billetera")				
		return data

	def create(self, validated_data):
		type_wallet = Type_Wallet.objects.get(pk=self.context["request"].data['type_wallet'])
		wallet = Wallet(
			wallet = validated_data['wallet'],
			type_wallet = type_wallet,
		)
		if self.context["request"].user.groups.filter(pk=4).exists():
			wallet.user = self.context["request"].user
		else:
			wallet.balance = validated_data['balance']

		wallet.save()
		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():
			wallet_chashiers = self.context["request"].POST.getlist('cashiers[]')
			for obj in wallet_chashiers:
				user = User.objects.get(pk=obj)
				wallet_chashier = Wallet_Cashier(
					wallet = wallet,
					cashier = user,
					type_wallet = type_wallet
				)
				wallet_chashier.save()			
		# coin = Coin.objects.get(pk=1)
		# cwallet = Coin_Wallet(
		# 	coin = coin,
		# 	wallet = wallet
		# )		
		# cwallet.save()
		return wallet

	def update(self, instance, validated_data):
		instance.wallet = validated_data.get('wallet', instance.wallet)
		type_wallet = Type_Wallet.objects.get(pk=self.context["request"].data['type_wallet'])
		instance.type_wallet = type_wallet
		instance.active = validated_data.get('active', instance.active)

		if not self.context["request"].user.groups.filter(Q(pk=3) | Q(pk=4)).exists():

			chashiersD = Wallet_Cashier.objects.filter(wallet=instance.id).delete()
			wallet_chashiers = self.context["request"].data.getlist('cashiers[]')
			for obj in wallet_chashiers:
				user = User.objects.get(pk=obj)
				wallet_chashier = Wallet_Cashier(
					wallet = instance,
					cashier = user,
					type_wallet = type_wallet
				)
				wallet_chashier.save()	

		instance.save()
		return instance
		
	def get_cashiers(self, obj):
		cashiers = Wallet_Cashier.objects.filter(wallet = obj)
		if len(cashiers):
			us = list()
			for obj in cashiers:
				us.append(obj.cashier) 
			return CUserSerializer(us, many=True).data
		return None
	def get_type_wallet(self, obj):
		return Type_Wallet_Serializer(obj.type_wallet).data		

	def get_user(self, obj):
		if obj.user != None:
			return CUserSerializer(obj.user).data				
		return None

class Financial_EntitySerializer(serializers.ModelSerializer):
	class Meta:
		model = Financial_Entity
		fields = ('id','financial_entity',)
		write_only_fields = ()
		read_only_fields = ()  		

class Transaction_TypeSerializer(serializers.ModelSerializer):
	coin_1 = serializers.SerializerMethodField()
	coin_2 = serializers.SerializerMethodField()
	financial_entity_1 = serializers.SerializerMethodField()
	financial_entity_2 = serializers.SerializerMethodField()
	class Meta:
		model = Transaction_Type
		fields = ('id', 'transaction_type', 'coin_1', 'financial_entity_1', 'coin_2', 'financial_entity_2', 'transaction_commission', 'cashier_commission', 'active','exchange_rate')
		write_only_fields = ('deleted')
		read_only_fields = ()    			

	def create(self, validated_data):
		coin_1 = Coin.objects.get(pk=self.context["request"].data.get('coin_1'))
		coin_2 = Coin.objects.get(pk=self.context["request"].data.get('coin_2'))
		financial_entity_1 = Financial_Entity.objects.get(pk=self.context["request"].data.get('financial_entity_1'))
		financial_entity_2 = Financial_Entity.objects.get(pk=self.context["request"].data.get('financial_entity_2'))
		transaction_type = Transaction_Type(
			transaction_type = validated_data['transaction_type'],
			coin_1 = coin_1,
			financial_entity_1 = financial_entity_1,
			coin_2 = coin_2,
			financial_entity_2 = financial_entity_2,
			transaction_commission = validated_data['transaction_commission'],
			cashier_commission = validated_data['cashier_commission'],
			exchange_rate = validated_data['exchange_rate']
		)
		transaction_type.save()
		return transaction_type

	def update(self, instance, validated_data):
		# instance.transaction_type = validated_data.get('transaction_type', instance.transaction_type)
		instance.transaction_commission = validated_data.get('transaction_commission', instance.transaction_commission)
		instance.cashier_commission = validated_data.get('cashier_commission', instance.cashier_commission)
		# coin_1 = Coin.objects.get(pk=self.context["request"].data.get('coin_1'))
		# coin_2 = Coin.objects.get(pk=self.context["request"].data.get('coin_2'))
		# financial_entity_1 = Financial_Entity.objects.get(pk=self.context["request"].data.get('financial_entity_1'))
		# financial_entity_2 = Financial_Entity.objects.get(pk=self.context["request"].data.get('financial_entity_2'))
		# instance.coin_1 = coin_1
		# instance.coin_2 = coin_2
		# instance.financial_entity_1 = financial_entity_1
		# instance.financial_entity_2 = financial_entity_2
		instance.exchange_rate = validated_data['exchange_rate']
		instance.active = 1 #validated_data.get('active', instance.active)
		instance.save()
		return instance		

	def validate(self, data):		
		if self.context["request"].method == "POST":		
			if not data.get('transaction_type'):
				raise serializers.ValidationError("Ingrese el Tipo de Transaccion")	

			if not self.context["request"].data.get('coin_1'):
				raise serializers.ValidationError("Seleccione la Moneda 1")	
			else:	
				try:
					coin_1 = Coin.objects.get(pk=self.context["request"].data.get('coin_1'))
				except Exception, e:
					raise serializers.ValidationError("Moneda 1 Invalida" )	

			if not self.context["request"].data.get('financial_entity_1'):
				raise serializers.ValidationError("Seleccione La Entidad Financiera de la Moneda 1")	
			else:	
				try:
					financial_entity_1 = Financial_Entity.objects.get(pk=self.context["request"].data.get('financial_entity_1'))
				except Exception, e:
					raise serializers.ValidationError("La Entidad Financiera de la Moneda 1 es Invalida" )	

			if not self.context["request"].data.get('coin_2'):
				raise serializers.ValidationError("Seleccione la Moneda 2")		
			else:	
				try:
					coin_2 = Coin.objects.get(pk=self.context["request"].data.get('coin_2'))
				except Exception, e:
					raise serializers.ValidationError("Moneda 2 Invalida")				


			if not self.context["request"].data.get('financial_entity_2'):
				raise serializers.ValidationError("Seleccione La Entidad Financiera de la Moneda 2")	
			else:	
				try:
					financial_entity_2 = Financial_Entity.objects.get(pk=self.context["request"].data.get('financial_entity_2'))
				except Exception, e:
					raise serializers.ValidationError("La Entidad Financiera de la Moneda 2 es Invalida" )	




		if not self.context["request"].data.get('exchange_rate'):
			raise serializers.ValidationError("Ingrese la Tarifa de Transaccion")	

		if not data.get('transaction_commission'):
			raise serializers.ValidationError("Ingrese la Cantidad de Comision de la Transaccion")

		if not data.get('cashier_commission'):
			raise serializers.ValidationError("Ingrese la Comision del Cajero")		

	
		# if self.context["request"].method == "PUT":
		# 	if not "active" in data:
		# 		raise serializers.ValidationError("Seleccione el Estatus")	

		try:
			if self.context["request"].method == "PUT":
				exist = Transaction_Type.objects.get(id != data.get('id'),coin_1=coin_1, coin_2 = coin_2, deleted = False)

			if self.context["request"].method == "POST":
				exist = Transaction_Type.objects.get(coin_1=coin_1, coin_2 = coin_2, deleted = False)

			if exist != None:
				raise serializers.ValidationError("El tipo de Transaccion ya Existe")			
		except Exception, e:
			pass			

		return data

	def get_coin_1(self, obj):
		return Coin_Serializer(obj.coin_1).data

	def get_coin_2(self, obj):
		return Coin_Serializer(obj.coin_2).data

	def get_financial_entity_1(self, obj):
		return Financial_EntitySerializer(obj.financial_entity_1).data

	def get_financial_entity_2(self, obj):
		return Financial_EntitySerializer(obj.financial_entity_2).data

	def get_exchange_rate(self, obj):
		exchange_rates = Exchange_Rate.objects.filter(transaction_type = obj.id)
		if len(exchange_rates):
			return Exchange_RateSerializer(exchange_rates, many=True).data		
		return None				

class Transaction_Status_IndicatorSerializer(serializers.ModelSerializer):
	transactions = serializers.SerializerMethodField()
	class Meta:
		model = Transaction_Status
		fields = ('id', 'transaction_status', 'transactions',)
		write_only_fields = ()
		read_only_fields = ()  

	def get_transactions(self, obj):
		if self.context["request"].user.groups.filter(Q(pk=1) | Q(pk=2)).exists():
			return len(Transaction.objects.filter(transaction_status = obj))
		elif self.context["request"].user.groups.filter(pk=3).exists():
			return len(Transaction.objects.filter(transaction_status = obj, cashier = self.context["request"].user))
		else: 
			return -1

class Transaction_StatusSerializer(serializers.ModelSerializer):
	class Meta:
		model = Transaction_Status
		fields = ('id', 'transaction_status',)
		write_only_fields = ()
		read_only_fields = ()  

class Transaction_LogSerializer(serializers.ModelSerializer):
	transaction_status = serializers.SerializerMethodField()
	class Meta:
		model = Transaction_Log
		fields = ('transaction_status', 'cashier', 'comment', 'date',)
		write_only_fields = ('id',)
		read_only_fields = ()  	

	def validate(self, data):			
		if not data.get('transaction_type'):
			raise serializers.ValidationError("Ingrese el Tipo de Transaccion")

	def get_transaction_status(self, obj):
		return Transaction_StatusSerializer(obj.transaction_status).data

class Transaction_ConfirmSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	class Meta:
		model = Transaction_Confirm
		fields = ('id', 'date', 'quantity', 'code_confirmation', 'financial_entity', 'user')
		write_only_fields = ('id', 'transaction', 'type')
		read_only_fields = ()  	

	def create(self, validated_data):
		tc = Transaction_Confirm(
			code_confirmation = self.context["request"].data.get('code_confirmation'),
			user = self.context["request"].user,
			transaction = self.context["transaction"],
			type = self.context["type"]
		)
		# if 'date' in self.context["request"].data:
		# 	if self.context["request"].data.get('date') != None:
		# 		tc.date = self.context["request"].data.get('date')

		# if 'quantity' in self.context["request"].data:
		# 	if self.context["request"].data.get('quantity') != None:				
		# 		tc.quantity = self.context["request"].data.get('quantity')

		# if 'financial_entity' in self.context["request"].data:
		# if self.context["flag"]:
		# 	ef = self.context["request"].data.get('financial_entity')
		# else:
		# 	if self.context["transaction"].transaction_type.financial_entity_2.id == 1:
		# 		ef = self.context["transaction"].bank_2.bank
		# 	else:			
		# 		ef = self.context["transaction"].type_wallet_2.type_wallet		
			# tc.financial_entity = ef
		tc.save()
		return tc

	def validate(self, data):			
		# if not self.context["request"].data.get('date'):
		# 	raise serializers.ValidationError("Ingrese la Fecha del Deposito/Transaccion")

		# if not self.context["request"].data.get('quantity'):
		# 	raise serializers.ValidationError("Ingrese la Cantidad del Deposito/Transaccion")

		# if self.context["flag"]:
		# 	if not self.context["request"].data.get('financial_entity'):
		# 		raise serializers.ValidationError("Ingrese la Entidad Financiera del Deposito/Transaccion")	

		if not data.get('code_confirmation'):
			raise serializers.ValidationError("Ingrese el Numero de Recibo del Deposito/Transaccion")	
		return data

		
	
	def get_user(self, obj):
		return CUserSerializer(obj.user).data

class TransactionSerializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	cashier = serializers.SerializerMethodField()
	transaction_status = serializers.SerializerMethodField()
	transaction_type = serializers.SerializerMethodField()
	bank_1 = serializers.SerializerMethodField()
	bank_2 = serializers.SerializerMethodField()
	wallet_1 = serializers.SerializerMethodField()
	wallet_2 = serializers.SerializerMethodField()
	# wallet = serializers.SerializerMethodField()
	commission_detail = serializers.SerializerMethodField()
	transaction_confirm = serializers.SerializerMethodField()
	class Meta:
		model = Transaction
		fields = ('id', 'code', 'quantity', 'user', 'cashier', 'transaction_status', 'transaction_type', 'bank_1', 'bank_2',  'wallet_1', 'wallet_2',  'date', 'commission_detail', 'transaction_confirm', 'ef1_commission', 'ef2_commission',) #'wallet',
		write_only_fields = ('code_coin_1', 'code_coin_2', 'cashier_commission', 'transaction_commission', 'exchange_rate', 'ef1_commission', 'ef2_commission')
		read_only_fields = () 

	def create(self, validated_data):
		status = Transaction_Status.objects.get(pk=1)
		transaction_type = Transaction_Type.objects.get(pk=self.context["request"].data['transaction_type'])
		ef1_commission = 0
		ef2_commission = 0

		if transaction_type.financial_entity_1.id == 1:
			wallet_1 = None
			bank_1 = Bank.objects.get(pk=self.context["request"].data.get('bank_1'))
			ef1_commission = bank_1.bank.commission
		else:			
			wallet_1 = Wallet.objects.get(pk=self.context["request"].data.get('wallet_1'))
			bank_1 = None
			ef1_commission = wallet_1.type_wallet.commission
			
		if transaction_type.financial_entity_2.id == 1:
			wallet_2 = None
			bank_2 = Bank.objects.get(pk=self.context["request"].data.get('bank_2'))			
			ef2_commission = bank_2.bank.commission
		else:			
			wallet_2 = Wallet.objects.get(pk=self.context["request"].data['wallet_2'])
			bank_2 = None			
			ef2_commission = wallet_2.type_wallet.commission

		transaction = Transaction(
			code = uuid.uuid4().hex.lower(),
			quantity = validated_data['quantity'],
			user = self.context["request"].user,
			transaction_status = status,
			transaction_type = transaction_type,
			bank_1 = bank_1,
			bank_2 = bank_2,
			ef1_commission = ef1_commission,
			ef2_commission = ef2_commission,
			wallet_1 = wallet_1,
			wallet_2 = wallet_2,
			code_coin_1 = transaction_type.coin_1.code,
			code_coin_2 = transaction_type.coin_2.code,
			exchange_rate = transaction_type.exchange_rate,
			cashier_commission = transaction_type.cashier_commission,
			transaction_commission = transaction_type.transaction_commission,									
		)
		transaction.save()
		tlog = Transaction_Log(
			transaction = transaction,
			transaction_status = status,
			comment = "System Log"
		)		
		tlog.save()
		return transaction

	def validate(self, data):			
		exist_transaction = Transaction.objects.filter(user = self.context["request"].user).exclude(transaction_status__id__in = [5,6])
		if len(exist_transaction) > 0:
			raise serializers.ValidationError("No se puede crear la Transaccion, ya que tiene una en curso")

		if not self.context["request"].data.get('quantity'):
			raise serializers.ValidationError("Ingrese la Cantidad")

		if not self.context["request"].data.get('transaction_type'):
			raise serializers.ValidationError("Seleccione el Tipo de Transaccion")		
		else:
			try:
				tt = Transaction_Type.objects.get(pk=self.context["request"].data['transaction_type'])	
			except Exception, e:
				raise serializers.ValidationError("Tipo de Transaccion Invalido")

		if tt.financial_entity_1.id == 1:
			if not self.context["request"].data.get('bank_1'):
				raise serializers.ValidationError("Seleccione El Banco de la Moneda 1: " + tt.coin_1.coin)	
			else:
				try:
					tw_1_1 = Bank.objects.get(pk=self.context["request"].data['bank_1'])	
					if tw_1_1.user != None:
						raise serializers.ValidationError("El Banco de la Moneda 1: " + tt.coin_1.coin +", es Invalido")
				except Exception, e:
					raise serializers.ValidationError("El Banco de la Moneda 1: " + tt.coin_1.coin +", es Invalido")
		else:			
			if not self.context["request"].data.get('wallet_1'):
				raise serializers.ValidationError("Seleccione la Billetera de la Moneda 1: " + tt.coin_1.coin)		
			else:
				try:
					tw_1_2 = Wallet.objects.get(pk=self.context["request"].data['wallet_1'])	
					if tw_1_2.user != None:
						raise serializers.ValidationError("El Banco de la Moneda 1: " + tt.coin_1.coin +", es Invalido")						
				except Exception, e:
					raise serializers.ValidationError("La Billetera de la Moneda 1: " + tt.coin_1.coin +", es Invalido")

		if tt.financial_entity_2.id == 1:
			if not self.context["request"].data.get('bank_2'):
				raise serializers.ValidationError("Seleccione El Banco de la Moneda 2: " + tt.coin_2.coin)	
			else:
				try:
					tw_2_1 = Bank.objects.get(pk=self.context["request"].data['bank_2'])					
				except Exception, e:
					raise serializers.ValidationError("El Banco de la Moneda 2: " + tt.coin_2.coin +", es Invalido")
		else:			
			if not self.context["request"].data.get('wallet_2'):
				raise serializers.ValidationError("Seleccione la Billetera de la Moneda 2: " + tt.coin_2.coin)		
			else:
				try:
					tw_2_2 = Wallet.objects.get(pk=self.context["request"].data['wallet_2'])	
				except Exception, e:
					raise serializers.ValidationError("La Billetera de la Moneda 2: " + tt.coin_2.coin +", es Invalido")		

		return data

	def get_transaction_confirm(self, obj):
		# tc = Transaction_Confirm.objects.filter(transaction = obj)
		trans = Transaction_Confirm.objects.filter(transaction = obj, user = obj.user).exclude(code_confirmation = '')
		if len(trans) > 0:
			c1 = trans.reverse()[0].code_confirmation
		else:
			c1 = None

		dep = Transaction_Confirm.objects.filter(transaction = obj, type = 'CAJERO').exclude(code_confirmation = '')
		if len(dep) > 0:
			c2 = dep.reverse()[0].code_confirmation
		else:
			c2 = None		
		return {'deposito' : c2, 'transferencia' :c1  } #Transaction_ConfirmSerializer(tc, many = True).data

	def get_user(self, obj):
		return CUserSerializer(obj.user).data

	def get_cashier(self, obj):
		if obj.cashier != None:
			return CUserSerializer(obj.cashier).data	
		return None
		
	def get_transaction_status(self, obj):
		return Transaction_StatusSerializer(obj.transaction_status).data

	def get_transaction_type(self, obj):
		return Transaction_TypeSerializer(obj.transaction_type).data		

	def get_bank_1(self, obj):
		if obj.bank_1 != None:
			return BankSerializer(obj.bank_1).data	
		return None			

	def get_bank_2(self, obj):
		if obj.bank_2 != None:
			return BankSerializer(obj.bank_2).data							
		return None			
		
	def get_wallet_1(self, obj):
		if obj.wallet_1 != None:
			return WalletSerializer(obj.wallet_1).data		

	def get_wallet_2(self, obj):
		if obj.wallet_2 != None:
			return WalletSerializer(obj.wallet_2).data		
		return None			

	# def get_wallet(self, obj):
	# 	if obj.cashier != None:
	# 		if obj.wallet != None:
	# 			return WalletSerializer(obj.wallet).data									
	# 	return None				

	def get_commission_detail(self, obj):
		cant = obj.quantity
		quantity = cant / obj.transaction_type.exchange_rate
		comi_1 = (obj.transaction_commission *  quantity) / 100
		comi_2 = (obj.cashier_commission *  quantity) / 100
		comi_3 = (obj.ef1_commission *  quantity) / 100
		comi_4 = (obj.ef2_commission *  quantity) / 100
		total_comi = comi_1 + comi_2 + comi_3 + comi_4
		payment_total = quantity + total_comi 
		if obj.transaction_status.id != 5:
			return {'payment_total': round(payment_total, 2),'exchange_total' : round(quantity, 2), 'exchange_transaction_commission' : round(total_comi, 2), 'exchange_quantity': round(cant, 2) }		
		else:
			return {'cashier_commission': round(comi_2, 2), 'transaction_commission': round(comi_1, 2), 'payment_total': round(payment_total, 2),'exchange_total' : round(quantity, 2), 'exchange_transaction_commission' : round(total_comi, 2), 'exchange_quantity': round(cant, 2) }		

class Notification_Type_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Notification_Type
		fields = ('id', 'type',)
		write_only_fields = ()
		read_only_fields = ()    

class Notification_Serializer(serializers.ModelSerializer):
	user = serializers.SerializerMethodField()
	type = serializers.SerializerMethodField()
	transaction = serializers.SerializerMethodField()
	class Meta:
		model = Notification
		fields = ('id', 'transaction', 'user', 'type', 'viewed', 'date', 'title')
		write_only_fields = ()
		read_only_fields = ()   		

	def get_type(self, obj):
		return Notification_Type_Serializer(obj.type).data		

	def get_user(self, obj):
		return CUserSerializer(obj.user).data		

	def get_transaction(self, obj):
		if obj.transaction != None:
			return TransactionSerializer(obj.transaction).data
		return None					