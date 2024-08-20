import os
import subprocess
import shutil
from datetime import datetime

# Colores
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Variables
DEFAULT_DOCKER_REGISTRY_PORT = 5000
MAX_PORT_ATTEMPTS = 10
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
REGISTRY_CONTAINER_NAME = f"registry_{timestamp}"
REGISTRY_IMAGE_NAME = f"localhost:{timestamp}/my-python-app"
PYTHON_APP_DIR = "my-python-app"

def run_command(command, success_message, error_message):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"{Colors.OKGREEN}{success_message}{Colors.ENDC}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        if "bind: address already in use" in e.stderr:
            return "port_in_use"
        else:
            print(f"{Colors.FAIL}{error_message}: {e.stderr}{Colors.ENDC}")
            exit(1)

def is_port_available(port):
    try:
        result = subprocess.run(f"ss -tuln | grep :{port}", shell=True, capture_output=True, text=True)
        return result.stdout == ""
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}Error al verificar el puerto: {e.stderr}{Colors.ENDC}")
        return False

def find_available_port(start_port, max_attempts):
    port = start_port
    for attempt in range(max_attempts):
        if is_port_available(port):
            return port
        else:
            print(f"{Colors.WARNING}Puerto {port} está en uso. Intentando con el puerto {port + 1}...{Colors.ENDC}")
            port += 1
    print(f"{Colors.FAIL}No se encontró un puerto disponible después de {max_attempts} intentos.{Colors.ENDC}")
    exit(1)

def show_docker_status():
    print(f"{Colors.HEADER}Mostrando contenedores y imágenes disponibles...{Colors.ENDC}")
    print(f"{Colors.OKCYAN}Contenedores creados:{Colors.ENDC}")
    containers = run_command("docker ps -a", "Contenedores listados correctamente", "Error al listar contenedores")
    print(containers)

    print(f"{Colors.OKCYAN}Imágenes disponibles:{Colors.ENDC}")
    images = run_command("docker images", "Imágenes listadas correctamente", "Error al listar imágenes")
    print(images)

def main():
    # 1. Instalar Docker
    print(f"{Colors.HEADER}Instalando Docker...{Colors.ENDC}")
    if shutil.which("docker") is None:
        print(f"{Colors.WARNING}Docker no encontrado. Instalando Docker...{Colors.ENDC}")
        run_command("sudo apt update", "Actualización completada", "Error al actualizar")
        run_command("sudo apt install -y apt-transport-https ca-certificates curl software-properties-common",
                    "Paquetes instalados correctamente", "Error al instalar paquetes")
        run_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -",
                    "Clave GPG añadida", "Error al añadir la clave GPG")
        run_command('sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"',
                    "Repositorio añadido", "Error al añadir el repositorio")
        run_command("sudo apt update", "Actualización completada", "Error al actualizar")
        run_command("sudo apt install -y docker-ce", "Docker instalado correctamente", "Error al instalar Docker")
        run_command("sudo systemctl start docker", "Docker iniciado", "Error al iniciar Docker")
        run_command("sudo systemctl enable docker", "Docker habilitado en el inicio", "Error al habilitar Docker en el inicio")
    else:
        print(f"{Colors.OKBLUE}Docker ya está instalado.{Colors.ENDC}")

    # 2. Encontrar un puerto disponible y ejecutar Docker Registry
    print(f"{Colors.HEADER}Buscando un puerto disponible para Docker Registry...{Colors.ENDC}")
    available_port = find_available_port(DEFAULT_DOCKER_REGISTRY_PORT, MAX_PORT_ATTEMPTS)
    print(f"{Colors.OKCYAN}Puerto disponible encontrado: {available_port}{Colors.ENDC}")

    print(f"{Colors.HEADER}Ejecutando Docker Registry con nombre personalizado...{Colors.ENDC}")
    run_command(f"docker run -d -p {available_port}:5000 --name {REGISTRY_CONTAINER_NAME} registry:2",
                f"Docker Registry {REGISTRY_CONTAINER_NAME} ejecutándose en el puerto {available_port}",
                "Error al ejecutar Docker Registry")

    # 3. Crear y construir la aplicación Python
    print(f"{Colors.HEADER}Creando y construyendo la aplicación Python...{Colors.ENDC}")
    os.makedirs(PYTHON_APP_DIR, exist_ok=True)

    with open(f"{PYTHON_APP_DIR}/Dockerfile", "w") as dockerfile:
        dockerfile.write("""
        FROM python:3.9-slim

        WORKDIR /app

        COPY app.py /app/app.py

        CMD ["python", "/app/app.py"]
        """)
        print(f"{Colors.OKGREEN}Dockerfile creado.{Colors.ENDC}")

    with open(f"{PYTHON_APP_DIR}/app.py", "w") as app_file:
        app_file.write('print("Hello from Docker Registry!")')
        print(f"{Colors.OKGREEN}Archivo app.py creado.{Colors.ENDC}")

    # Usar el nombre del registro local
    run_command(f"docker build -t {REGISTRY_IMAGE_NAME} {PYTHON_APP_DIR}",
                "Imagen de Docker construida correctamente", "Error al construir la imagen de Docker")

    # 4. Subir la imagen al Docker Registry
    print(f"{Colors.HEADER}Subiendo la imagen al Docker Registry...{Colors.ENDC}")
    run_command(f"docker push {REGISTRY_IMAGE_NAME}",
                "Imagen subida correctamente al Docker Registry", "Error al subir la imagen al Docker Registry")

    # 5. Ejecutar la imagen directamente desde el Docker Registry
    print(f"{Colors.HEADER}Ejecutando la aplicación desde el Docker Registry...{Colors.ENDC}")
    run_command(f"docker run --rm {REGISTRY_IMAGE_NAME}",
                "Aplicación ejecutada correctamente", "Error al ejecutar la aplicación")

    # 6. Mostrar estado de Docker
    show_docker_status()

    # 7. Limpiar (opcional)
    print(f"{Colors.HEADER}Deteniendo y eliminando el contenedor del Docker Registry...{Colors.ENDC}")
    run_command(f"docker stop {REGISTRY_CONTAINER_NAME} && docker rm {REGISTRY_CONTAINER_NAME}",
                f"Docker Registry {REGISTRY_CONTAINER_NAME} detenido y eliminado", "Error al detener y eliminar Docker Registry")

    print(f"{Colors.OKGREEN}Proceso completado.{Colors.ENDC}")

if __name__ == "__main__":
    main()
