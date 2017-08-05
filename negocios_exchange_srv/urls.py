"""negocios_exchange_srv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, patterns, include
from django.contrib.auth.models import User, Group
from django.contrib import admin
admin.autodiscover()
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import permissions, routers, serializers, viewsets

from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope

from negocios_exchange import views 
# from negocios_exchange.vistas_negocios_exchange import login 



# Routers provide an easy way of automatically determining the URL conf
router = routers.SimpleRouter()



urlpatterns = [
    # url(r'^user$', views.UserView.as_view()),
    url(r'^user$', views.UserListView.as_view()),
    url(r'^auth/activation/(?P<token>[\w-]+)$', views.Verify_UserViewSet.as_view()),
    url(r'^auth/reset/(?P<token>[\w-]+)$', views.Password_ResetViewSet.as_view()),
    url(r'^auth/recovery$', views.Password_RecoveryViewSet.as_view()),
    url(r'^user/(?P<pk>[0-9]+)$', views.UserView.as_view()),
    url(r'^user/public$', views.UserPublicViewSet.as_view()),
    url(r'^user/profile$', views.ProfileViewSet.as_view()),
    url(r'^user/cashiers$', views.CashiersViewSet.as_view()),
    url(r'^countries$', views.CountryViewSet.as_view()),
    url(r'^auth/token$', views.LoginView.as_view()),
    url(r'^accounts/', admin.site.urls),
    url(r'^admin/', admin.site.urls),
    # url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # url(r'^user$', views.UserView.as_view()),
    url(r'^account_type', views.Account_TypeViewSet.as_view()),
    url(r'^coins$', views.CoinViewSet.as_view()),
    url(r'^groups$', views.GroupViewSet.as_view()),
    url(r'^type_wallet$', views.Type_WalletListViewSet.as_view()),
    url(r'^financial_entity$', views.Financial_EntityViewSet.as_view()),
    url(r'^type_wallet/(?P<pk>[0-9]+)/wallet$', views.Type_WalletViewSet.as_view()), 
    url(r'^type_wallet/(?P<pk>[0-9]+)$', views.Wallet_TypeUpViewSet.as_view()), 
    url(r'^bank$', views.BankListViewSet.as_view()),
    url(r'^bank/type$', views.Bank_TypeListViewSet.as_view()),
    url(r'^bank/type/(?P<pk>[0-9]+)$', views.Bank_TypeUpViewSet.as_view()),
    url(r'^bank/(?P<pk>[0-9]+)$', views.BankViewSet.as_view()),
    url(r'^wallet$', views.WalletListViewSet.as_view()),
    url(r'^wallet/(?P<pk>[0-9]+)$', views.WalletViewSet.as_view()),    
    url(r'^transaction_type$', views.Transaction_TypeListViewSet.as_view()),
    url(r'^transaction_type/(?P<pk>[0-9]+)$', views.Transaction_TypeViewSet.as_view()), 
    url(r'^transaction$', views.TransactionListViewSet.as_view()),      
    url(r'^transaction/(?P<pk>[0-9]+)$', views.TransactionViewSet.as_view()), 
    url(r'^transaction/new$', views.Transactions_CreatedViewSet.as_view()),      
    url(r'^transaction/(?P<pk>[0-9]+)/take$', views.Transactions_CreatedViewSet.as_view()), 
    url(r'^transaction/(?P<pk>[0-9]+)/confirm$', views.Transactions_ConfirmViewSet.as_view()), 
    url(r'^transaction/(?P<pk>[0-9]+)/reject$', views.Transactions_RejectViewSet.as_view()), 
    url(r'^transaction/(?P<pk>[0-9]+)/dispute$', views.Transactions_DisputeViewSet.as_view()), 
    url(r'^transaction/(?P<pk>[0-9]+)/status/(?P<st>[0-9]+)$', views.Transactions_Change_StatusViewSet.as_view()), 
    url(r'^transaction/status$', views.EstatusViewSet.as_view()), 
    url(r'^transaction/counter$', views.Estatus_IndicatorViewSet.as_view()), 
    url(r'^transaction/ranking$', views.RankingViewSet.as_view()), 
    url(r'^transaction/active$', views.Transactions_Active.as_view()), 
    # url(r'^$',  views.HomePageView.as_view(), name='home'),
    # url(r'^', include('negocios_exchange.urls', namespace='negocios_exchange')),
    url(r'^push$', views.PushView.as_view()), 
    url(r'^notification$', views.NotificationVierSet.as_view()), 
    url(r'^notification/(?P<pk>[0-9]+)$', views.NotificationVierSet.as_view()), 
    url(r'^mail$', views.EmailView.as_view()), 

]
urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns) 
  