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
DOCKER_REGISTRY_PORT = 5000
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
IMAGE_NAME = f"localhost:{DOCKER_REGISTRY_PORT}/registry_{timestamp}"
PYTHON_APP_DIR = "my-python-app"

def run_command(command, success_message, error_message):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"{Colors.OKGREEN}{success_message}{Colors.ENDC}")
    except subprocess.CalledProcessError:
        print(f"{Colors.FAIL}{error_message}{Colors.ENDC}")
        exit(1)

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

    # 2. Ejecutar Docker Registry
    print(f"{Colors.HEADER}Ejecutando Docker Registry...{Colors.ENDC}")
    run_command(f"docker run -d -p {DOCKER_REGISTRY_PORT}:5000 --name registry registry:2",
                "Docker Registry ejecutándose", "Error al ejecutar Docker Registry")

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

    run_command(f"docker build -t {IMAGE_NAME} {PYTHON_APP_DIR}",
                "Imagen de Docker construida correctamente", "Error al construir la imagen de Docker")

    # 4. Subir la imagen al Docker Registry
    print(f"{Colors.HEADER}Subiendo la imagen al Docker Registry...{Colors.ENDC}")
    run_command(f"docker push {IMAGE_NAME}",
                "Imagen subida correctamente al Docker Registry", "Error al subir la imagen al Docker Registry")

    # 5. Ejecutar la imagen directamente desde el Docker Registry
    print(f"{Colors.HEADER}Ejecutando la aplicación desde el Docker Registry...{Colors.ENDC}")
    run_command(f"docker run --rm {IMAGE_NAME}",
                "Aplicación ejecutada correctamente", "Error al ejecutar la aplicación")

    # 6. Limpiar (opcional)
    print(f"{Colors.HEADER}Deteniendo y eliminando el contenedor del Docker Registry...{Colors.ENDC}")
    run_command("docker stop registry && docker rm registry",
                "Docker Registry detenido y eliminado", "Error al detener y eliminar Docker Registry")

    print(f"{Colors.OKGREEN}Proceso completado.{Colors.ENDC}")

if __name__ == "__main__":
    main()
