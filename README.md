# demo_api_django-rest-framework

Casa de Cambio Online

Web Api Demo Django Rest Framework, enfocada en una casa de cambio de dividas online.


Para su uso debe asegurarse de tener instaladas todas las dependencias del archivo: requirements.txt

Configurar el archivo negocios_exchange_srv/settings.py con sus credenciales de PostgreSQL (Lin. 96 y 97)

Luego sincronzar la base de datos: python manage.py migrate

Instalar todos los fixtures: python manage.py loaddata {nombre_del_sixture}

Y por ultimo correr el servidor: python manage.py runserver

