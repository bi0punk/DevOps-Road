#!/bin/bash

# Variables
DOCKER_REGISTRY_PORT=5000
IMAGE_NAME="localhost:$DOCKER_REGISTRY_PORT/my-python-app"
PYTHON_APP_DIR="my-python-app"

# 1. Instalar Docker
echo "Instalando Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker no encontrado. Instalando Docker..."
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt update
    sudo apt install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
else
    echo "Docker ya está instalado."
fi

# 2. Ejecutar Docker Registry
echo "Ejecutando Docker Registry..."
docker run -d -p $DOCKER_REGISTRY_PORT:5000 --name registry registry:2

# 3. Crear y construir la aplicación Python
echo "Creando y construyendo la aplicación Python..."
mkdir -p $PYTHON_APP_DIR
cat <<EOF > $PYTHON_APP_DIR/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY app.py /app/app.py

CMD ["python", "/app/app.py"]
EOF

cat <<EOF > $PYTHON_APP_DIR/app.py
print("Hello from Docker Registry!")
EOF

cd $PYTHON_APP_DIR
docker build -t $IMAGE_NAME .

# 4. Subir la imagen al Docker Registry
echo "Subiendo la imagen al Docker Registry..."
docker tag $IMAGE_NAME $IMAGE_NAME
docker push $IMAGE_NAME

# 5. Ejecutar la imagen directamente desde el Docker Registry
echo "Ejecutando la aplicación desde el Docker Registry..."
docker run --rm $IMAGE_NAME

echo "Proceso completado."

# 6. Limpiar (opcional)
echo "Deteniendo y eliminando el contenedor del Docker Registry..."
docker stop registry
docker rm registry