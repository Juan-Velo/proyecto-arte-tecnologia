from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
import os

app = Flask(__name__)

# Variables globales
camera = None
face_cascade = None

# Intentar cargar el clasificador de rostros
try:
    # Intentar múltiples rutas posibles para el clasificador
    cascade_paths = [
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
        'haarcascade_frontalface_default.xml',
        './haarcascade_frontalface_default.xml'
    ]
    
    for path in cascade_paths:
        try:
            face_cascade = cv2.CascadeClassifier(path)
            if not face_cascade.empty():
                print(f"Clasificador de rostros cargado correctamente desde: {path}")
                break
        except:
            continue
    
    if face_cascade is None or face_cascade.empty():
        print("ADVERTENCIA: No se pudo cargar el clasificador de rostros. La detección facial no funcionará.")
        face_cascade = None
        
except Exception as e:
    print(f"Error al inicializar clasificador: {str(e)}")
    face_cascade = None

def calcular_agotamiento(respuestas):
    """
    Calcula el porcentaje de agotamiento basado en las actividades realizadas.
    Retorna un valor entre 0 y 100.
    """
    puntaje_total = 0
    
    # Puntajes para cada actividad (más alto = más agotamiento)
    puntajes = {
        'horas_trabajo': {
            '0-2': 5,
            '3-4': 15,
            '5-6': 25,
            '7-8': 40,
            '9+': 60
        },
        'ejercicio': {
            'ninguno': 0,
            'ligero': 10,
            'moderado': 20,
            'intenso': 35
        },
        'horas_sueno': {
            '0-3': 40,
            '4-5': 30,
            '6-7': 10,
            '8+': 0
        },
        'estres': {
            'bajo': 5,
            'medio': 15,
            'alto': 30,
            'muy_alto': 45
        },
        'tiempo_pantalla': {
            '0-2': 5,
            '3-5': 15,
            '6-8': 25,
            '9+': 35
        },
        'comidas': {
            '0-1': 15,
            '2': 5,
            '3': 0,
            '4+': 10
        }
    }
    
    # Calcular puntaje total
    for categoria, valor in respuestas.items():
        if categoria in puntajes and valor in puntajes[categoria]:
            puntaje_total += puntajes[categoria][valor]
    
    # Normalizar a un porcentaje entre 0 y 100
    max_posible = 215  # Suma máxima posible de todos los puntajes
    porcentaje_agotamiento = min(100, (puntaje_total / max_posible) * 100)
    
    return round(porcentaje_agotamiento, 1)

def crear_imagen_abstracta(porcentaje_agotamiento):
    """
    Crea una imagen abstracta con diseño de batería VERTICAL de celular.
    Arriba = agotamiento (B&N), Abajo = energía (color).
    """
    # Crear imagen base VERTICAL (más alta que ancha)
    ancho, altura = 400, 600
    img = np.zeros((altura, ancho, 3), dtype=np.uint8)
    
    # Calcular línea divisoria
    # porcentaje_energia = lo que queda disponible (abajo, a color)
    porcentaje_energia = 100 - porcentaje_agotamiento
    linea_division = int(altura * (porcentaje_agotamiento / 100))
    
    # Parte de AGOTAMIENTO (ARRIBA) - tonos grises y oscuros
    if linea_division > 0:
        for y in range(linea_division):
            for x in range(ancho):
                # Crear patrón de agotamiento con ruido y gradientes oscuros
                noise = np.random.randint(0, 40)
                gray_value = int(30 + ((y / linea_division) * 80)) + noise
                gray_value = min(255, max(0, gray_value))
                img[y, x] = [gray_value, gray_value, gray_value]
    
    # Parte de ENERGÍA (ABAJO) - colores vibrantes
    if linea_division < altura:
        for y in range(linea_division, altura):
            for x in range(ancho):
                # Crear patrón de energía con colores vibrantes
                hue = ((y - linea_division) / (altura - linea_division)) * 120 + 100  # Verde-azul
                saturation = 70 + np.random.randint(0, 30)
                value = 80 + np.random.randint(0, 40)
                
                # Convertir HSV a RGB
                h = (hue % 360) / 360.0
                s = saturation / 100.0
                v = value / 100.0
                
                c = v * s
                x_color = c * (1 - abs((h * 6) % 2 - 1))
                m = v - c
                
                if 0 <= h < 1/6:
                    r, g, b = c, x_color, 0
                elif 1/6 <= h < 2/6:
                    r, g, b = x_color, c, 0
                elif 2/6 <= h < 3/6:
                    r, g, b = 0, c, x_color
                elif 3/6 <= h < 4/6:
                    r, g, b = 0, x_color, c
                elif 4/6 <= h < 5/6:
                    r, g, b = x_color, 0, c
                else:
                    r, g, b = c, 0, x_color
                
                img[y, x] = [
                    int((r + m) * 255),
                    int((g + m) * 255),
                    int((b + m) * 255)
                ]
    
    # Agregar línea divisoria horizontal
    if 0 < linea_division < altura:
        cv2.line(img, (0, linea_division), (ancho, linea_division), (255, 255, 255), 4)
    
    # Crear diseño de batería VERTICAL estilo celular
    margen = 30
    ancho_borde = 8
    ancho_punta = int(ancho * 0.4)  # Punta en la parte superior (40% del ancho)
    altura_punta = 20  # Altura de la punta
    
    # Crear canvas más grande (espacio para la punta arriba)
    altura_total = altura + margen * 2 + altura_punta
    ancho_total = ancho + margen * 2
    imagen_bateria = np.ones((altura_total, ancho_total, 3), dtype=np.uint8) * 50  # Fondo oscuro
    
    # Colocar la imagen en el centro (dejando espacio arriba para la punta)
    imagen_bateria[margen + altura_punta:margen + altura_punta + altura, margen:margen + ancho] = img
    
    # Color del borde basado en el nivel de ENERGÍA
    if porcentaje_energia > 70:
        color_borde = (0, 255, 0)  # Verde
    elif porcentaje_energia > 40:
        color_borde = (0, 255, 255)  # Amarillo
    elif porcentaje_energia > 20:
        color_borde = (0, 165, 255)  # Naranja
    else:
        color_borde = (0, 0, 255)  # Rojo
    
    # Dibujar rectángulo principal de la batería
    cv2.rectangle(imagen_bateria, 
                  (margen - ancho_borde, margen + altura_punta - ancho_borde),
                  (margen + ancho + ancho_borde, margen + altura_punta + altura + ancho_borde),
                  color_borde, ancho_borde)
    
    # Dibujar punta de la batería (ARRIBA, centrada horizontalmente)
    punta_x_inicio = margen + (ancho // 2) - (ancho_punta // 2)
    punta_y_inicio = margen
    cv2.rectangle(imagen_bateria,
                  (punta_x_inicio, punta_y_inicio),
                  (punta_x_inicio + ancho_punta, punta_y_inicio + altura_punta),
                  color_borde, -1)
    
    # Agregar porcentaje de energía en la ESQUINA SUPERIOR DERECHA
    font = cv2.FONT_HERSHEY_SIMPLEX
    texto_porcentaje = f'{porcentaje_energia:.0f}%'
    text_size = cv2.getTextSize(texto_porcentaje, font, 1.5, 4)[0]
    text_x = ancho_total - text_size[0] - 15  # 15 píxeles desde el borde derecho
    text_y = 55  # Cerca del borde superior
    
    cv2.putText(imagen_bateria, texto_porcentaje, (text_x, text_y),
                font, 1.5, color_borde, 4)
    
    # Convertir a base64
    success, encoded_img = cv2.imencode('.png', imagen_bateria)
    if success:
        img_base64 = base64.b64encode(encoded_img.tobytes()).decode()
        return f"data:image/png;base64,{img_base64}"
    else:
        # Imagen de fallback
        img = np.full((600, 300, 3), [100, 100, 100], dtype=np.uint8)
        cv2.putText(img, 'Sin imagen disponible', (50, 300), font, 1, (255, 255, 255), 2)
        success, encoded_img = cv2.imencode('.png', img)
        img_base64 = base64.b64encode(encoded_img.tobytes()).decode()
        return f"data:image/png;base64,{img_base64}"

def procesar_imagen_con_agotamiento(imagen_base64, porcentaje_agotamiento):
    """
    Procesa la imagen dividiéndola en color y blanco y negro.
    Añade fecha y hora en la esquina superior izquierda.
    """
    # Decodificar imagen base64
    img_data = base64.b64decode(imagen_base64.split(',')[1])
    img = Image.open(BytesIO(img_data))
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)
    
    altura, ancho = img_array.shape[:2]
    
    # Calcular línea divisoria
    linea_division = int(altura * (porcentaje_agotamiento / 100))
    
    # Crear imagen resultado
    resultado = img_array.copy()
    
    # Convertir la parte superior a blanco y negro
    if linea_division > 0:
        parte_bn = cv2.cvtColor(img_array[:linea_division, :], cv2.COLOR_RGB2GRAY)
        resultado[:linea_division, :] = cv2.cvtColor(parte_bn, cv2.COLOR_GRAY2RGB)
    
    # Agregar línea divisoria
    if 0 < linea_division < altura:
        cv2.line(resultado, (0, linea_division), (ancho, linea_division), (255, 255, 255), 2)
    
    # Convertir a PIL para agregar texto
    resultado_pil = Image.fromarray(resultado)
    draw = ImageDraw.Draw(resultado_pil)
    
    # Obtener fecha y hora actual
    fecha_hora = datetime.now()
    texto_fecha = fecha_hora.strftime("%d/%m/%Y")
    texto_hora = fecha_hora.strftime("%I:%M %p")
    
    # Calcular tamaño de fuente basado en el tamaño de la imagen
    font_size = max(int(altura * 0.035), 20)  # Mínimo 20px
    
    try:
        # Intentar cargar una fuente elegante (Arial Bold)
        font_fecha = ImageFont.truetype("arialbd.ttf", font_size)
        font_hora = ImageFont.truetype("arial.ttf", int(font_size * 0.85))
    except:
        try:
            # Fallback a fuentes del sistema
            font_fecha = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", font_size)
            font_hora = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(font_size * 0.85))
        except:
            # Si no hay fuentes disponibles, usar default
            font_fecha = ImageFont.load_default()
            font_hora = ImageFont.load_default()
    
    # Posición en esquina superior izquierda
    padding = int(ancho * 0.03)  # 3% del ancho como padding
    x_pos = padding
    y_pos_fecha = padding
    
    # Calcular altura del texto
    bbox_fecha = draw.textbbox((0, 0), texto_fecha, font=font_fecha)
    altura_fecha = bbox_fecha[3] - bbox_fecha[1]
    y_pos_hora = y_pos_fecha + altura_fecha + 5
    
    # Color llamativo con borde para mejor visibilidad
    color_texto = (255, 215, 0)  # Dorado/Amarillo brillante
    color_borde = (0, 0, 0)  # Negro para el borde
    
    # Dibujar borde del texto (sombra)
    offset = 2
    for adj_x in range(-offset, offset + 1):
        for adj_y in range(-offset, offset + 1):
            draw.text((x_pos + adj_x, y_pos_fecha + adj_y), texto_fecha, font=font_fecha, fill=color_borde)
            draw.text((x_pos + adj_x, y_pos_hora + adj_y), texto_hora, font=font_hora, fill=color_borde)
    
    # Dibujar texto principal
    draw.text((x_pos, y_pos_fecha), texto_fecha, font=font_fecha, fill=color_texto)
    draw.text((x_pos, y_pos_hora), texto_hora, font=font_hora, fill=color_texto)
    
    # Convertir de vuelta a array y luego a base64
    resultado_array = np.array(resultado_pil)
    resultado_final = Image.fromarray(resultado_array)
    buffered = BytesIO()
    resultado_final.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultado')
def resultado():
    return render_template('resultado.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analiza la foto capturada y genera una visualización de energía usando los datos del formulario.
    """
    try:
        datos = request.json
        photo_data = datos.get('photo', '')
        respuestas = datos.get('respuestas', {})
        
        if not photo_data or not photo_data.startswith('data:image'):
            return jsonify({'success': False, 'error': 'No se proporcionó una imagen válida'}), 400
        
        if not respuestas:
            return jsonify({'success': False, 'error': 'No se proporcionaron respuestas del formulario'}), 400
        
        # Calcular el porcentaje de agotamiento usando las respuestas del formulario
        porcentaje_agotamiento = calcular_agotamiento(respuestas)
        porcentaje_energia = 100 - porcentaje_agotamiento
        
        # Procesar la imagen
        imagen_procesada = procesar_imagen_con_agotamiento(photo_data, porcentaje_agotamiento)
        
        # Extraer solo el base64 sin el prefijo data:image
        if imagen_procesada.startswith('data:image/png;base64,'):
            image_base64 = imagen_procesada.split(',')[1]
        else:
            image_base64 = imagen_procesada
        
        return jsonify({
            'success': True,
            'energy_percentage': porcentaje_energia,
            'image_data': image_base64,
            'message': generar_mensaje_reflexivo(porcentaje_agotamiento)
        })
    
    except Exception as e:
        print(f"Error en analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/procesar_encuesta', methods=['POST'])
def procesar_encuesta():
    try:
        datos = request.json
        respuestas = datos.get('respuestas', {})
        imagen = datos.get('imagen', '')
        
        porcentaje_agotamiento = calcular_agotamiento(respuestas)
        porcentaje_energia = 100 - porcentaje_agotamiento
        
        if imagen and imagen.startswith('data:image'):
            imagen_procesada = procesar_imagen_con_agotamiento(imagen, porcentaje_agotamiento)
        else:
            return jsonify({'success': False, 'error': 'No se proporcionó imagen.'}), 400

        return jsonify({
            'success': True,
            'porcentaje_energia': porcentaje_energia,
            'imagen_procesada': imagen_procesada,
            'mensaje': generar_mensaje_reflexivo(porcentaje_agotamiento)
        })
    
    except Exception as e:
        print(f"Error en procesar_encuesta: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generar_mensaje_reflexivo(porcentaje_agotamiento):
    """
    Genera un mensaje reflexivo basado en el nivel de agotamiento.
    """
    if porcentaje_agotamiento < 20:
        return "Tu energía brilla con intensidad. ¿Cómo mantienes este equilibrio?"
    elif porcentaje_agotamiento < 40:
        return "Aún hay luz en tu interior. Recuerda nutrir tu esencia."
    elif porcentaje_agotamiento < 60:
        return "Las sombras comienzan a extenderse. Es momento de reflexionar sobre tus límites."
    elif porcentaje_agotamiento < 80:
        return "El agotamiento consume gran parte de ti. ¿Qué puedes soltar?"
    else:
        return "La oscuridad predomina. Tu ser necesita atención y cuidado urgente."

@app.route('/video_feed')
def video_feed():
    """
    Ruta para el stream de video de la cámara.
    Nota: Esta función ya no se usa activamente para evitar conflictos con la cámara.
    Se mantiene por compatibilidad pero retorna una imagen estática.
    """
    def generate():
        try:
            # Crear una imagen simple de placeholder
            img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(img, "Camara no disponible", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            ret, buffer = cv2.imencode('.jpg', img)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error en video_feed: {str(e)}")
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detectar_persona')
def detectar_persona():
    """
    Verifica si hay una persona frente a la cámara.
    Ahora solo retorna información para control manual.
    """
    return jsonify({
        'persona_detectada': False, 
        'mensaje': 'Usa el botón "Continuar Manualmente" para iniciar la experiencia'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
