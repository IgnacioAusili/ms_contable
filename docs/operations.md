Por el momento, este proyecto no tiene CI/CD automatizado. Se documentan aca los criterios y 
los pasos que se realizan manualmente.

# Releases

- Validar que pasan exitosamente todos los tests.

- Cambiar la version en el Proyecto (`settings.VERSION`)

- Hacer un squash de todas las migraciones de BD durante el desarrollo de la nueva version \
Importante: solo de la nueva version, dejar las migraciones de versiones previas. \
Eliminar las migraciones intermedias que son propias de la etapa de desarrollo, pero que no fueron lanzadas
para que usen los usuarios. \
Deberia haber, como maximo, una migracion por cada version que se lanza. \
`python manage.py squashmigrations <app> <start_migration> <end_migration>`

- Generar imagen Docker y subirla a [Dockerhub](https://hub.docker.com/repository/docker/matiasschulz/ms_contable/tags)
    - El dockerfile deberia ejecutar todos los tests

- Generar Tag con la version en el repositorio de Github

- Generar Release, con sus artefactos y release notes, en el repositorio de Github \
Artefactos:
    - Release notes
    - Archivos minimos para instalacion/uso
    - Codigo fuente

# Extras

### Comandos utiles de Django

```shell
python manage.py startapp {app_name}
python manage.py makemigrations
python manage.py makemigrations --empty <nombre_app>
python manage.py migrate
python manage.py migrate zero
python manage.py migrate zero --fake
python manage.py migrate 0001
python manage.py createsuperuser
python manage.py runserver
python manage.py squashmigrations {app_name} {start_migration} {end_migration}
python manage.py shell; # importlib
python manage.py test
```
