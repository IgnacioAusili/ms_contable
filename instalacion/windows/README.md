# Instalador nativo de Windows

El instalador usa Inno Setup, un runtime de Python embebido y Caddy. No requiere Docker. Está localizado en español y solicita permisos de administrador para instalar los binarios en `Program Files` y registrar el nombre local en `hosts`.

## Preparar y compilar

Ejecutá `build.ps1` desde PowerShell con CPython x64 3.11.9 a 3.13. El script prepara el runtime embebido, instala las dependencias de `requirements-windows.txt`, compila el bytecode de Python para que el runtime de `Program Files` no tenga que regenerarlo en cada inicio, copia el código fuente sin datos locales y genera los archivos estáticos. Busca Inno Setup en `.tools` o en el `PATH`; si está en otra ubicación, indicá su ruta con `-InnoCompiler`. Caddy se reutiliza desde `build\caddy` o se descarga desde el sitio oficial junto con su licencia.

La versión del instalador se toma de `APP_VERSION` en `ms_contable/settings.py`. El ejecutable queda en `dist\https\MSContable-Setup-version.exe`.

## HTTPS local

Caddy y Waitress escuchan solo en loopback y reciben puertos aleatorios altos al iniciar. El acceso HTTPS usa `https://mscontable:<puerto>` y Waitress queda interno, sin exposición en la red local. Los puertos elegidos se conservan mientras ambos servicios sigan activos; no se recorren listas de puertos fijos. El instalador agrega `mscontable` al archivo `hosts` de Windows apuntando a `127.0.0.1` y `::1`; al desinstalar, quita únicamente el bloque que agregó. El panel administrativo de Caddy está desactivado.

Durante la instalación, el instalador agrega la autoridad certificadora local de Caddy al almacén `Root` del usuario actual, sin abrir el aviso de confianza de Windows. El certificado y su clave privada se conservan bajo `%LOCALAPPDATA%\MSContable\caddy`; el desinstalador quita la confianza y elimina esa carpeta. La base SQLite y los logs permanecen bajo `%LOCALAPPDATA%\MSContable\data` y `%LOCALAPPDATA%\MSContable\logs`. La clave secreta de Django se genera una vez y se conserva en `%LOCALAPPDATA%\MSContable\config\django-secret-key`.

Al inicializar y actualizar la aplicación, el instalador limita los permisos de `%LOCALAPPDATA%\MSContable` a la cuenta actual, `SYSTEM` y administradores. La regla se aplica a los archivos y subcarpetas existentes. En aperturas posteriores, el lanzador comprueba la marca de versión y los permisos de la carpeta raíz; solo vuelve a recorrer los datos si detecta que hay que reparar o actualizar la protección.

Al abrir MS Contable desde un acceso directo, aparece primero una pantalla de carga servida por un proceso mínimo de Python en una dirección loopback y un puerto efímero. Esa página no accede a la base ni a los secretos; consulta únicamente el estado de inicio y redirige al login cuando Django, Caddy y HTTPS responden. Mientras haya páginas del admin abiertas, estas notifican actividad local; al cerrar la última, el lanzador detiene Waitress y Caddy. Si se vuelve a pulsar el acceso durante una sesión activa, se abre directamente el login existente. Si falta la confianza del certificado, el lanzador instala el certificado existente mientras Caddy sigue funcionando, sin iniciarlo una segunda vez. La reparación registra su salida en `%LOCALAPPDATA%\MSContable\logs\https-repair.log`.

El detalle de tiempos y etapas de cada inicio queda en `%LOCALAPPDATA%\MSContable\logs\startup.log`; los registros de Waitress, Caddy y la página de carga se guardan en esa misma carpeta. Todos los servidores locales escuchan exclusivamente en loopback.

La configuración inicial permite importar opcionalmente una base anterior y aplicar las migraciones. No abre una consola ni solicita crear el usuario administrador: la primera cuenta se crea desde la página de bienvenida al abrir MS Contable. Las casillas para crear accesos directos en el menú Inicio y en el escritorio son independientes; la opción de abrir la app al finalizar también lo es.

El acceso **Desinstalar MS Contable** queda dentro de la carpeta de instalación; no se crea en el menú Inicio ni en el escritorio. Durante una desinstalación interactiva hay dos opciones: conservar los datos, o eliminarlos junto con sus registros. Las desinstalaciones silenciosas conservan los datos.

El certificado local habilita HTTPS entre el navegador y Caddy. Caddy reenvía a Waitress por HTTP en loopback; ambos puertos están limitados a este equipo.
