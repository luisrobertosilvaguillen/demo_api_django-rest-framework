from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.contrib.auth.models import User, Group

class Country(models.Model):
	name = models.CharField(max_length=200, default='')

class User_Profile(models.Model):
	uid =  models.CharField(max_length=40, default='')
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usero')
	dni = models.CharField(max_length=15, default='')
	phone_1 = models.CharField(max_length=20, default='')
	phone_2 = models.CharField(max_length=20, default='')
	verified = models.BooleanField(default=False)
	deleted = models.BooleanField(default=False)
	birthdate = models.DateTimeField(null = True)
	country = models.ForeignKey(Country, on_delete=models.CASCADE, null = True)

class Type_Token(models.Model):
	id = models.AutoField(primary_key=True)
	type_token = models.CharField(max_length=40)

class Token_Verification(models.Model):
	type_token = models.ForeignKey(Type_Token, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	token = models.CharField(max_length=60)
	active = models.BooleanField(default=True)

class Coin(models.Model):
	id = models.AutoField(primary_key=True)
	code = models.CharField(max_length=5, default='')
	coin = models.CharField(max_length=40)

class Bank_Type(models.Model):
	id = models.AutoField(primary_key=True)
	bank = models.CharField(max_length=60)		
	commission = models.FloatField(null = True)	

class Account_Type(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.CharField(max_length=10)		
				
class Bank(models.Model):
	id = models.AutoField(primary_key=True)
	bank = models.ForeignKey(Bank_Type, on_delete=models.CASCADE, related_name='bank_1')	
	account = models.CharField(max_length=20, default='')				
	account_owner = models.CharField(max_length=100, null = True, default='')				
	account_dni = models.CharField(max_length=20, null = True, default='')				
	account_email = models.CharField(max_length=100, null = True, default='')				
	account_type = models.ForeignKey(Account_Type, null = True, on_delete=models.CASCADE)
	balance = models.FloatField(null = True, default=0)				
	user = models.ForeignKey(User, null = True, on_delete=models.CASCADE, related_name='user_2')
	active = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)

class Bank_Cashier(models.Model):
	bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
	cashier = models.ForeignKey(User, on_delete=models.CASCADE)


class Type_Wallet(models.Model):
	id = models.AutoField(primary_key=True)
	code = models.CharField(max_length=30)			
	url_icon = models.CharField(max_length=60)			
	type_wallet = models.CharField(max_length=60)			
	commission = models.FloatField(null = True)	

class Wallet(models.Model):
	id = models.AutoField(primary_key=True)
	type_wallet = models.ForeignKey(Type_Wallet, on_delete=models.CASCADE)
	wallet = models.CharField(max_length=60)		
	balance = models.FloatField(default=0)	
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userw', null = True)
	active = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)

class Wallet_Cashier(models.Model):
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
	cashier = models.ForeignKey(User, on_delete=models.CASCADE)	
	type_wallet = models.ForeignKey(Type_Wallet, on_delete=models.CASCADE, null = True)

class Coin_Wallet(models.Model):
	coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)

class Financial_Entity(models.Model):
	id = models.AutoField(primary_key=True)
	financial_entity =models.CharField(max_length=20)

class Transaction_Type(models.Model):
	id = models.AutoField(primary_key=True)
	transaction_type = models.CharField(max_length=80)	
	coin_1 = models.ForeignKey(Coin, related_name='coin_1')
	financial_entity_1 = models.ForeignKey(Financial_Entity, null = True, related_name='financial_entity_1', on_delete=models.CASCADE)
	coin_2 = models.ForeignKey(Coin, related_name='coin_2')
	financial_entity_2 = models.ForeignKey(Financial_Entity, null = True, related_name='financial_entity_2', on_delete=models.CASCADE)
	transaction_commission = models.FloatField()	
	cashier_commission = models.FloatField()	
	active = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)
	exchange_rate = models.FloatField(null = True)	

class Transaction_Status(models.Model):
	id = models.AutoField(primary_key=True)
	transaction_status = models.CharField(max_length=50)	

class Transaction(models.Model):
	id = models.AutoField(primary_key=True)
	code = models.CharField(max_length=50, default= '')
	quantity = models.FloatField(default=0)	
	transaction_commission = models.FloatField()	
	ef1_commission = models.FloatField(null = True)	
	ef2_commission = models.FloatField(null = True)	
	transaction_commission = models.FloatField()	
	cashier_commission = models.FloatField()		
	exchange_rate = models.FloatField()	
	code_coin_1 = models.CharField(max_length=5)
	code_coin_2 = models.CharField(max_length=5)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
	cashier = models.ForeignKey(User, on_delete=models.CASCADE, default = None, null = True, related_name='cashier')
	transaction_status = models.ForeignKey(Transaction_Status, on_delete=models.CASCADE, related_name='cashier')
	transaction_type = models.ForeignKey(Transaction_Type, on_delete=models.CASCADE)	
	bank_1 = models.ForeignKey(Bank, on_delete=models.CASCADE, null = True, related_name='bank_1')
	bank_2 = models.ForeignKey(Bank, on_delete=models.CASCADE, null = True, related_name='bank_2')
	wallet_1 = models.ForeignKey(Wallet, on_delete=models.CASCADE, default = None, null = True, related_name='_wallet_1_')
	wallet_2 = models.ForeignKey(Wallet, on_delete=models.CASCADE, default = None, null = True, related_name='_wallet_2_')
	# wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, default = None, null = True, related_name='wallet_1')		
	date = models.DateTimeField(auto_now_add=True)


class Transaction_Confirm(models.Model):
	id = models.AutoField(primary_key=True)
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
	date = models.DateTimeField(null = True)
	quantity = models.FloatField(default=0, null = True)	
	code_confirmation = models.CharField(max_length=50, default= '')
	financial_entity = models.CharField(max_length=80, default= '', null = True)
	type = models.CharField(max_length=30, default= '', null = True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_confirm')

class Transaction_Log(models.Model):
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
	transaction_status = models.ForeignKey(Transaction_Status, on_delete=models.CASCADE, related_name='cashiers')
	cashier = models.ForeignKey(User, on_delete=models.CASCADE, default = None, null = True)
	comment = models.CharField(max_length=255)
	date = models.DateTimeField(auto_now_add=True)

class Notification_Type(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.CharField(max_length=50, default= '')

class Notification(models.Model):
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null = True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_noti')
	type = models.ForeignKey(Notification_Type, on_delete=models.CASCADE)
	viewed = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=200, default= '', null = True)
