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

# Variables
DEFAULT_DOCKER_REGISTRY_PORT = 5000
MAX_PORT_ATTEMPTS = 10
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
REGISTRY_CONTAINER_NAME = f"registry_{timestamp}"
REGISTRY_IMAGE_NAME = f"localhost:{DEFAULT_DOCKER_REGISTRY_PORT}/my-python-app:latest"
PYTHON_APP_DIR = "my-python-app"

def run_command(command, success_message, error_message, check=True):
    """ Ejecuta un comando y maneja errores. """
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        print(f"{Colors.OKGREEN}{success_message}{Colors.ENDC}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}{error_message}: {e.stderr}{Colors.ENDC}")
        if "bind: address already in use" in e.stderr:
            return "port_in_use"
        exit(1)

def is_port_available(port):
    command = f"ss -tuln | grep :{port}"
    return not run_command(command, "", "", check=False)

def find_available_port(start_port, max_attempts):
    for attempt in range(max_attempts):
        if is_port_available(start_port):
            return start_port
        print(f"{Colors.WARNING}Puerto {start_port} está en uso. Intentando el puerto {start_port + 1}...{Colors.ENDC}")
        start_port += 1
    print(f"{Colors.FAIL}No se encontró un puerto disponible después de {max_attempts} intentos.{Colors.ENDC}")
    exit(1)

def show_docker_status():
    print(f"{Colors.HEADER}Mostrando contenedores y imágenes disponibles...{Colors.ENDC}")
    containers = run_command("docker ps -a", "Contenedores listados correctamente", "Error al listar contenedores", check=False)
    images = run_command("docker images", "Imágenes listadas correctamente", "Error al listar imágenes", check=False)
    print(f"{Colors.OKCYAN}Contenedores creados:{Colors.ENDC}\n{containers}")
    print(f"{Colors.OKCYAN}Imágenes disponibles:{Colors.ENDC}\n{images}")

def install_docker():
    if shutil.which("docker") is None:
        print(f"{Colors.WARNING}Docker no encontrado. Instalando Docker...{Colors.ENDC}")
        run_command("sudo apt update", "Actualización completada", "Error al actualizar")
        run_command("sudo apt install -y apt-transport-https ca-certificates curl software-properties-common", "Paquetes instalados correctamente", "Error al instalar paquetes")
        run_command("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -", "Clave GPG añadida", "Error al añadir la clave GPG")
        run_command('sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"', "Repositorio añadido", "Error al añadir el repositorio")
        run_command("sudo apt update", "Actualización completada", "Error al actualizar")
        run_command("sudo apt install -y docker-ce", "Docker instalado correctamente", "Error al instalar Docker")
        run_command("sudo systemctl start docker", "Docker iniciado", "Error al iniciar Docker")
        run_command("sudo systemctl enable docker", "Docker habilitado en el inicio", "Error al habilitar Docker en el inicio")
    else:
        print(f"{Colors.OKBLUE}Docker ya está instalado.{Colors.ENDC}")

def create_and_build_app():
    print(f"{Colors.HEADER}Creando y construyendo la aplicación Python...{Colors.ENDC}")
    os.makedirs(PYTHON_APP_DIR, exist_ok=True)

    dockerfile_content = """
    FROM python:3.9-slim

    WORKDIR /app

    COPY app.py /app/app.py

    CMD ["python", "/app/app.py"]
    """
    with open(f"{PYTHON_APP_DIR}/Dockerfile", "w") as dockerfile:
        dockerfile.write(dockerfile_content)
        print(f"{Colors.OKGREEN}Dockerfile creado.{Colors.ENDC}")

    app_content = 'print("Hello from Docker Registry!")'
    with open(f"{PYTHON_APP_DIR}/app.py", "w") as app_file:
        app_file.write(app_content)
        print(f"{Colors.OKGREEN}Archivo app.py creado.{Colors.ENDC}")

    run_command(f"docker build -t {REGISTRY_IMAGE_NAME} {PYTHON_APP_DIR}", "Imagen de Docker construida correctamente", "Error al construir la imagen de Docker")

def main():
    install_docker()

    print(f"{Colors.HEADER}Buscando un puerto disponible para Docker Registry...{Colors.ENDC}")
    available_port = find_available_port(DEFAULT_DOCKER_REGISTRY_PORT, MAX_PORT_ATTEMPTS)
    print(f"{Colors.OKCYAN}Puerto disponible encontrado: {available_port}{Colors.ENDC}")

    print(f"{Colors.HEADER}Ejecutando Docker Registry con nombre personalizado...{Colors.ENDC}")
    run_command(f"docker run -d -p {available_port}:5000 --name {REGISTRY_CONTAINER_NAME} registry:2", f"Docker Registry {REGISTRY_CONTAINER_NAME} ejecutándose en el puerto {available_port}", "Error al ejecutar Docker Registry")

    create_and_build_app()

    print(f"{Colors.HEADER}Subiendo la imagen al Docker Registry...{Colors.ENDC}")
    run_command(f"docker push {REGISTRY_IMAGE_NAME}", "Imagen subida correctamente al Docker Registry", "Error al subir la imagen al Docker Registry")

    print(f"{Colors.HEADER}Ejecutando la aplicación desde el Docker Registry...{Colors.ENDC}")
    run_command(f"docker run --rm {REGISTRY_IMAGE_NAME}", "Aplicación ejecutada correctamente", "Error al ejecutar la aplicación")

    show_docker_status()

    print(f"{Colors.HEADER}Deteniendo y eliminando el contenedor del Docker Registry...{Colors.ENDC}")
    run_command(f"docker stop {REGISTRY_CONTAINER_NAME} && docker rm {REGISTRY_CONTAINER_NAME}", f"Docker Registry {REGISTRY_CONTAINER_NAME} detenido y eliminado", "Error al detener y eliminar Docker Registry")

    print(f"{Colors.OKGREEN}Proceso completado.{Colors.ENDC}")

if __name__ == "__main__":
    main()
