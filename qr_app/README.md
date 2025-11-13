# Generador de Código QR para URLs

Esta aplicación web permite generar códigos QR a partir de URLs de aplicaciones web multiplataforma. Al escanear el QR, se redirige a la URL proporcionada.

## Instalación

1. Navega a la carpeta `qr_app`:
   ```
   cd qr_app
   ```

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la aplicación:
   ```
   python app.py
   ```

2. Abre tu navegador y ve a `http://127.0.0.1:5000/`

3. Ingresa la URL de tu aplicación web en el campo proporcionado.

4. Haz clic en "Generar QR" para obtener el código QR.

5. Escanea el QR con cualquier lector de QR en laptop o celular para acceder a la URL.

## Despliegue en la nube

Para desplegar en la nube (ej. Heroku, AWS, etc.), configura el servidor web apropiado y sube los archivos. Asegúrate de que las dependencias estén instaladas en el entorno de producción.

## Características

- Interfaz responsive que funciona en laptop y celular.
- Generación rápida de códigos QR.
- Soporte para URLs válidas.