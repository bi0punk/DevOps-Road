#!/bin/bash

# Colores
HEADER='\033[95m'
OKBLUE='\033[94m'
OKCYAN='\033[96m'
OKGREEN='\033[92m'
WARNING='\033[93m'
FAIL='\033[91m'
ENDC='\033[0m'

# Variables
DEFAULT_DOCKER_REGISTRY_PORT=5000
MAX_PORT_ATTEMPTS=10
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REGISTRY_CONTAINER_NAME="registry_${TIMESTAMP}"
REGISTRY_IMAGE_NAME="localhost:${DEFAULT_DOCKER_REGISTRY_PORT}/my-python-app:latest"
PYTHON_APP_DIR="my-python-app"

run_command() {
    local command="$1"
    local success_message="$2"
    local error_message="$3"
    local check="$4"

    if [ "$check" = true ]; then
        if eval "$command"; then
            echo -e "${OKGREEN}${success_message}${ENDC}"
        else
            echo -e "${FAIL}${error_message}${ENDC}"
            exit 1
        fi
    else
        eval "$command" 2>/dev/null
    fi
}

is_port_available() {
    local port="$1"
    if ss -tuln | grep -q ":$port"; then
        return 1
    else
        return 0
    fi
}

find_available_port() {
    local start_port="$1"
    local max_attempts="$2"
    local port="$start_port"

    for ((attempt=1; attempt<=max_attempts; attempt++)); do
        if is_port_available "$port"; then
            echo "$port"
            return
        else
            echo -e "${WARNING}Puerto $port está en uso. Intentando el puerto $((port + 1))...${ENDC}"
            port=$((port + 1))
        fi
    done

    echo -e "${FAIL}No se encontró un puerto disponible después de $max_attempts intentos.${ENDC}"
    exit 1
}

show_docker_status() {
    echo -e "${HEADER}Mostrando contenedores y imágenes disponibles...${ENDC}"
    echo -e "${OKCYAN}Contenedores creados:${ENDC}"
    run_command "docker ps -a" "" "" false

    echo -e "${OKCYAN}Imágenes disponibles:${ENDC}"
    run_command "docker images" "" "" false
}

install_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${WARNING}Docker no encontrado. Instalando Docker...${ENDC}"
        run_command "sudo apt update" "Actualización completada" "Error al actualizar" true
        run_command "sudo apt install -y apt-transport-https ca-certificates curl software-properties-common" "Paquetes instalados correctamente" "Error al instalar paquetes" true
        run_command "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -" "Clave GPG añadida" "Error al añadir la clave GPG" true
        run_command 'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"' "Repositorio añadido" "Error al añadir el repositorio" true
        run_command "sudo apt update" "Actualización completada" "Error al actualizar" true
        run_command "sudo apt install -y docker-ce" "Docker instalado correctamente" "Error al instalar Docker" true
        run_command "sudo systemctl start docker" "Docker iniciado" "Error al iniciar Docker" true
        run_command "sudo systemctl enable docker" "Docker habilitado en el inicio" "Error al habilitar Docker en el inicio" true
    else
        echo -e "${OKBLUE}Docker ya está instalado.${ENDC}"
    fi
}

create_and_build_app() {
    echo -e "${HEADER}Creando y construyendo la aplicación Python...${ENDC}"
    mkdir -p "$PYTHON_APP_DIR"

    cat <<EOF > "$PYTHON_APP_DIR/Dockerfile"
FROM python:3.9-slim

WORKDIR /app

COPY app.py /app/app.py

CMD ["python", "/app/app.py"]
EOF
    echo -e "${OKGREEN}Dockerfile creado.${ENDC}"

    echo 'print("Hello from Docker Registry!")' > "$PYTHON_APP_DIR/app.py"
    echo -e "${OKGREEN}Archivo app.py creado.${ENDC}"

    run_command "docker build -t ${REGISTRY_IMAGE_NAME} ${PYTHON_APP_DIR}" "Imagen de Docker construida correctamente" "Error al construir la imagen de Docker" true
}

main() {
    install_docker

    echo -e "${HEADER}Buscando un puerto disponible para Docker Registry...${ENDC}"
    available_port=$(find_available_port "$DEFAULT_DOCKER_REGISTRY_PORT" "$MAX_PORT_ATTEMPTS")
    echo -e "${OKCYAN}Puerto disponible encontrado: $available_port${ENDC}"

    echo -e "${HEADER}Ejecutando Docker Registry con nombre personalizado...${ENDC}"
    run_command "docker run -d -p ${available_port}:5000 --name ${REGISTRY_CONTAINER_NAME} registry:2" "Docker Registry ${REGISTRY_CONTAINER_NAME} ejecutándose en el puerto ${available_port}" "Error al ejecutar Docker Registry" true

    create_and_build_app

    echo -e "${HEADER}Subiendo la imagen al Docker Registry...${ENDC}"
    run_command "docker push ${REGISTRY_IMAGE_NAME}" "Imagen subida correctamente al Docker Registry" "Error al subir la imagen al Docker Registry" true

    echo -e "${HEADER}Ejecutando la aplicación desde el Docker Registry...${ENDC}"
    run_command "docker run --rm ${REGISTRY_IMAGE_NAME}" "Aplicación ejecutada correctamente" "Error al ejecutar la aplicación" true

    show_docker_status

    echo -e "${HEADER}Deteniendo y eliminando el contenedor del Docker Registry...${ENDC}"
    run_command "docker stop ${REGISTRY_CONTAINER_NAME} && docker rm ${REGISTRY_CONTAINER_NAME}" "Docker Registry ${REGISTRY_CONTAINER_NAME} detenido y eliminado" "Error al detener y eliminar Docker Registry" true

    echo -e "${OKGREEN}Proceso completado.${ENDC}"
}

main
