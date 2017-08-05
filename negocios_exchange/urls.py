from django.conf.urls import patterns, url
# from negocios_exchange.vistas_negocios_exchange import login
from . import views
urlpatterns = patterns(
    url(r'^auth/token$', views.LoginView.as_view()),
)