from flask import Flask, request, render_template, jsonify
import psycopg2
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Servir archivos estáticos desde la carpeta `src` (para imágenes, etc.)
app = Flask(__name__, static_folder='src')

# Obtener la URL de la base de datos desde variables de entorno
DB_URL = os.getenv('DATABASE_URL')

if not DB_URL:
    raise ValueError(
        "DATABASE_URL no está configurada. "
        "Por favor, crea un archivo .env con DATABASE_URL=tu_url_de_base_de_datos"
    )

def get_connection():
    """Obtiene una conexión a la base de datos con manejo de errores."""
    try:
        return psycopg2.connect(DB_URL)
    except psycopg2.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise

@app.route('/')
def index():
    """Página principal que muestra los últimos registros."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT fecha_hora, peso_g FROM registros_peso ORDER BY id DESC LIMIT 10")
        datos = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', registros=datos)
    except Exception as e:
        print(f"Error al cargar la página principal: {e}")
        return render_template('index.html', registros=[], error="Error al cargar los datos")

@app.route('/insertar', methods=['POST'])
def insertar():
    """Inserta un nuevo registro de peso con validación."""
    try:
        # Validar que el request tenga JSON
        if not request.is_json:
            return jsonify({"error": "El contenido debe ser JSON"}), 400
        
        peso = request.json.get('peso')
        
        # Validaciones
        if peso is None:
            return jsonify({"error": "El campo 'peso' es requerido"}), 400
        
        try:
            peso = float(peso)
        except (ValueError, TypeError):
            return jsonify({"error": "El peso debe ser un número válido"}), 400
        
        if peso < 0:
            return jsonify({"error": "El peso no puede ser negativo"}), 400
        
        if peso > 1000000:  # Límite razonable de 1 tonelada
            return jsonify({"error": "El peso excede el límite permitido (1,000,000 g)"}), 400
        
        # Obtener la hora actual de Colombia (GMT-5, sin horario de verano)
        colombia_tz = timezone(timedelta(hours=-5))
        fecha_actual = datetime.now(colombia_tz)
        
        conn = get_connection()
        cur = conn.cursor()
        # Guardar la fecha con información de zona horaria
        cur.execute("INSERT INTO registros_peso (fecha_hora, peso_g) VALUES (%s, %s)", (fecha_actual, peso))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "mensaje": "Dato insertado correctamente",
            "peso": peso,
            "fecha": fecha_actual.strftime('%d/%m/%Y %H:%M')
        }), 201
        
    except psycopg2.Error as e:
        print(f"Error de base de datos: {e}")
        return jsonify({"error": "Error al guardar en la base de datos"}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/api/registros', methods=['GET'])
def obtener_registros():
    """Obtiene los últimos registros de peso."""
    try:
        # Obtener límite opcional desde query params
        limite = request.args.get('limite', default=10, type=int)
        if limite < 1 or limite > 100:
            limite = 10  # Límite por defecto y máximo
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT fecha_hora, peso_g FROM registros_peso ORDER BY id DESC LIMIT %s", (limite,))
        datos = cur.fetchall()
        cur.close()
        conn.close()
        
        # Zona horaria de Colombia
        colombia_tz = timezone(timedelta(hours=-5))
        
        # Convertir los datos a formato JSON
        registros_json = []
        for fecha, peso in datos:
            if fecha:
                # Si la fecha no tiene zona horaria, asumir que es UTC y convertir a Colombia
                if fecha.tzinfo is None:
                    fecha = fecha.replace(tzinfo=timezone.utc)
                # Convertir a zona horaria de Colombia
                fecha_colombia = fecha.astimezone(colombia_tz)
                fecha_str = fecha_colombia.strftime('%d/%m/%Y %H:%M')
            else:
                fecha_str = 'N/A'
                
            registros_json.append({
                'fecha': fecha_str,
                'peso': int(round(float(peso))) if peso else 0
            })
        
        return jsonify(registros_json)
        
    except Exception as e:
        print(f"Error al obtener registros: {e}")
        return jsonify({"error": "Error al obtener los registros"}), 500

@app.route('/api/indicadores', methods=['GET'])
def indicadores_reduccion():
    """Calcula indicadores simples de reducción con base en los registros.
    - baseline: primer valor registrado (g)
    - actual: último valor registrado (g)
    - reduccion_g: baseline - actual (no negativo)
    - reduccion_pct: porcentaje respecto al baseline
    - co2_kg_ev: conversión simple de residuos evitados a kgCO2e
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT peso_g FROM registros_peso ORDER BY id ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return jsonify({
                'baseline_g': 0,
                'actual_g': 0,
                'reduccion_g': 0,
                'reduccion_pct': 0.0,
                'co2_kg_ev': 0.0
            })

        valores = [float(r[0]) for r in rows if r[0] is not None]
        if not valores:
            return jsonify({
                'baseline_g': 0,
                'actual_g': 0,
                'reduccion_g': 0,
                'reduccion_pct': 0.0,
                'co2_kg_ev': 0.0
            })

        baseline_g = valores[0]
        actual_g = valores[-1]
        reduccion_g = max(0.0, baseline_g - actual_g)
        reduccion_pct = (reduccion_g / baseline_g * 100.0) if baseline_g > 0 else 0.0

        # Factor simple de conversión residuos (kg) -> CO2e (kg). Ajustable.
        CO2_FACTOR_KG_PER_KG = 1.2
        co2_kg_ev = (reduccion_g / 1000.0) * CO2_FACTOR_KG_PER_KG

        return jsonify({
            'baseline_g': round(baseline_g, 0),
            'actual_g': round(actual_g, 0),
            'reduccion_g': round(reduccion_g, 0),
            'reduccion_pct': round(reduccion_pct, 2),
            'co2_kg_ev': round(co2_kg_ev, 2)
        })
        
    except Exception as e:
        print(f"Error al calcular indicadores: {e}")
        return jsonify({
            'baseline_g': 0,
            'actual_g': 0,
            'reduccion_g': 0,
            'reduccion_pct': 0.0,
            'co2_kg_ev': 0.0,
            'error': 'Error al calcular indicadores'
        }), 500

@app.route('/test-hora')
def test_hora():
    colombia_tz = timezone(timedelta(hours=-5))
    hora_colombia = datetime.now(colombia_tz)
    hora_utc = datetime.now(timezone.utc)
    
    return jsonify({
        'hora_colombia': hora_colombia.strftime('%d/%m/%Y %H:%M:%S'),
        'hora_utc': hora_utc.strftime('%d/%m/%Y %H:%M:%S'),
        'diferencia_horas': 5
    })

if __name__ == '__main__':
    # Obtener configuración desde variables de entorno
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
