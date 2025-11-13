# proyecto-arte-tecnologia

Aplicación Flask para visualización de niveles de energía, desplegable en AWS Lambda usando Serverless Framework.

## Requisitos

- Python 3.12
- Serverless Framework
- AWS CLI configurado

## Instalación en EC2

```bash
# Clonar el repositorio
git clone git@github.com:Juan-Velo/proyecto-arte-tecnologia.git
cd proyecto-arte-tecnologia

# Desplegar con Serverless
sls deploy
```

## Estructura del Proyecto

- `app.py` - Aplicación Flask principal
- `wsgi_handler.py` - Handler para AWS Lambda
- `serverless.yml` - Configuración de Serverless Framework
- `requirements.txt` - Dependencias de Python
- `templates/` - Templates HTML
- `static/` - Archivos estáticos (CSS)
