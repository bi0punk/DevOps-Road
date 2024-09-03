# Docker Registry y Aplicación Python

Este proyecto incluye un script en Python que realiza las siguientes tareas:

1. **Instala Docker**: Si Docker no está instalado en el sistema, el script lo instalará.
2. **Encuentra un Puerto Disponible**: Busca un puerto disponible para ejecutar Docker Registry.
3. **Ejecuta Docker Registry**: Inicia un contenedor de Docker Registry en el puerto disponible.
4. **Crea y Construye una Aplicación Python**: Crea una aplicación Python simple y un `Dockerfile`, y construye una imagen Docker para la aplicación.
5. **Sube la Imagen al Docker Registry**: Suba la imagen construida al Docker Registry local.
6. **Ejecuta la Aplicación desde el Docker Registry**: Corre la aplicación desde el Docker Registry.
7. **Muestra el Estado de Docker**: Muestra el estado actual de los contenedores y las imágenes Docker.
8. **Limpieza**: Detiene y elimina el contenedor de Docker Registry.

## Requisitos

- Python 3.x
- Docker

## Instalación

1. Clona este repositorio:

    ```bash[
    git clonehttps://github.com/bi0punk/DevOps-Road 
    cd git clone    ```

2. Asegúrate de tener Python y Docker instalados. El script instalará Docker si no está presente.

## Uso

1. Ejecuta el script de Python:

    ```bash
    python script.py
    ```

    Donde `script.py` es el nombre del archivo del script de Python.

## Descripción del Script

### Colores

El script utiliza colores para mejorar la legibilidad del output en la terminal. Aquí están los códigos de color utilizados:

- `HEADER`: Azul claro
- `OKBLUE`: Azul
- `OKCYAN`: Cian
- `OKGREEN`: Verde
- `WARNING`: Amarillo
- `FAIL`: Rojo
- `ENDC`: Resetea el color

### Variables

- `DEFAULT_DOCKER_REGISTRY_PORT`: Puerto por defecto para el Docker Registry.
- `MAX_PORT_ATTEMPTS`: Número máximo de intentos para encontrar un puerto disponible.
- `timestamp`: Marca de tiempo para nombres únicos de contenedores e imágenes.
- `REGISTRY_CONTAINER_NAME`: Nombre del contenedor del Docker Registry.
- `REGISTRY_IMAGE_NAME`: Nombre de la imagen Docker construida.
- `PYTHON_APP_DIR`: Directorio donde se creará la aplicación Python.

### Funciones

- `run_command(command, success_message, error_message, check=True)`: Ejecuta un comando y maneja errores.
- `is_port_available(port)`: Verifica si un puerto está disponible.
- `find_available_port(start_port, max_attempts)`: Encuentra un puerto disponible.
- `show_docker_status()`: Muestra el estado de Docker (contenedores e imágenes).
- `install_docker()`: Instala Docker si no está instalado.
- `create_and_build_app()`: Crea y construye la aplicación Python.

### Ejecución

El script ejecuta una serie de pasos para configurar y probar Docker Registry, construir una aplicación Dockerizada y limpiar los recursos.

## Contribuciones

Si deseas contribuir a este proyecto, por favor, haz un fork del repositorio y envía un pull request con tus cambios.

## Licencia

Este proyecto está licenciado bajo los términos de la [Licencia MIT](LICENSE).

