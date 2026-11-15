# Hotel Paradise


Maestro, cuando descargue el trabajo, descomprima el archivo ZIP y ejecute el archivo correspondiente a su sistema operativo:

Windows: iniciar_windows.bat

macOS: iniciar_mac.command

El sistema instalará automáticamente las dependencias y se abrirá en su navegador.

Usuario: admin
Contraseña: admin

Es necesario tener Python instalado y mantener abierta la terminal mientras utiliza el sistema.


## Inicio rápido para la evaluación

1. Descarga y descomprime el ZIP del repositorio.
2. Con Python instalado, abre `iniciar_windows.bat` (Windows) o `iniciar_mac.command` (macOS). Si macOS no permite abrirlo, ejecuta `bash iniciar_mac.command` desde Terminal en la carpeta del proyecto.
3. Espera a que aparezca Hotel Paradise en tu navegador automáticamente. No cierres la ventana de la terminal mientras uses el sistema.
4. Inicia sesión con **usuario: admin** y **contraseña: admin**. Ambos datos aparecen también en la pantalla de inicio de sesión.

La primera ejecución puede tardar unos minutos mientras instala las dependencias. No hace falta instalar SQLite por separado. Si el navegador no se abre, usa la dirección que aparece en la terminal.

## Requisitos

- Python 3.11 o superior compatible con Django 5.2.
- No se necesita instalar un servidor de base de datos. SQLite crea su archivo local.
- No se necesita conexión a internet después de instalar los paquetes.

## Instalación

En macOS, abre Terminal en la carpeta del proyecto y ejecuta `bash iniciar_mac.command`. Si descargaste el código desde GitHub, el archivo puede no conservar su permiso ejecutable: con `bash` funciona sin cambiar los permisos. En Windows, abre `iniciar_windows.bat` para preparar la instalación automáticamente. También puedes seguir los comandos de abajo.

Si el puerto 8000 está ocupado, el instalador busca automáticamente otro puerto local libre y abre la dirección correcta. También puedes especificar un puerto, por ejemplo `bash iniciar_mac.command 8001` o `iniciar_windows.bat 8001`.

Desde una terminal ubicada en la raíz del proyecto:

### macOS / Linux

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py datos_demo
    python manage.py runserver

### Windows (PowerShell)

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe manage.py migrate
    .\.venv\Scripts\python.exe manage.py datos_demo
    .\.venv\Scripts\python.exe manage.py runserver

Abrir http://127.0.0.1:8000/ en el navegador.

Usuarios ficticios de demostración: **admin** (administrador), contraseña **admin**; **recepcion** (recepción), contraseña **ParadiseDemo2026!**. El panel de administración está en /admin/. Estas credenciales simples son para una demostración local; no exponer el servidor a internet ni usarlas en producción.

## Módulos

- habitaciones: inventario y fotografías.
- clientes: datos de huéspedes.
- reservaciones: CRUD, cancelación y búsqueda por fechas. La salida no ocupa la habitación durante esa noche.
- reportes: dashboard, estadísticas y reportes filtrables.
- seguridad: autenticación y acceso de personal; usuarios y permisos en Django Admin.
- config, templates y static: configuración e interfaz compartida.

Los ingresos muestran el valor total de las reservaciones no canceladas, no pagos efectivamente cobrados. Los datos de demostración son ficticios. Cada instalación tiene su propia base de datos en db.sqlite3. Las fotos cargadas por el personal viven en media/.

## Validaciones

Fechas en orden, habitaciones únicas, correos únicos, ausencia de solapamientos por habitación y rechazo de eliminación de habitaciones con reservaciones activas. Las reservas canceladas liberan sus fechas.


