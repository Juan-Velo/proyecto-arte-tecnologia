# proyecto-arte-tecnologia

Aplicación Flask para visualización de niveles de energía, desplegable en AWS Lambda usando Serverless Framework.

## Requisitos

- Docker 24+
- Serverless Framework
- AWS CLI configurado
- Credenciales IAM con permisos para ECR y Lambda

## Instalación en EC2

```bash
# Clonar el repositorio
git clone git@github.com:Juan-Velo/proyecto-arte-tecnologia.git
cd proyecto-arte-tecnologia

# Desplegar con Serverless (requiere Docker en ejecución)
export DOCKER_BUILDKIT=0   # garantiza un manifiesto compatible con Lambda
sls deploy
```

## Estructura del Proyecto

- `app.py` - Aplicación Flask principal
- `wsgi_handler.py` - Handler para AWS Lambda
- `serverless.yml` - Configuración de Serverless Framework (empaqueta una imagen en ECR)
- `requirements.txt` - Dependencias de Python (instaladas dentro del contenedor)
- `Dockerfile` / `.dockerignore` - Imagen y contexto de build para Lambda
- `templates/` - Templates HTML
- `static/` - Archivos estáticos (CSS)
