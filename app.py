from flask import Flask, request, render_template, jsonify
import psycopg2
from datetime import datetime, timezone, timedelta

# Servir archivos estáticos desde la carpeta `src` (para imágenes, etc.)
app = Flask(__name__, static_folder='src')

# 🔐 URL de conexión Neon (reemplaza con la tuya)
DB_URL = "postgresql://neondb_owner:npg_Gj8oXfSQmp3x@ep-solitary-rain-adsodwpc-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_connection():
    return psycopg2.connect(DB_URL)

@app.route('/')
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT fecha_hora, peso_g FROM registros_peso ORDER BY id DESC LIMIT 10")
    datos = cur.fetchall()
    conn.close()
    return render_template('index.html', registros=datos)

@app.route('/insertar', methods=['POST'])
def insertar():
    peso = request.json.get('peso')
    
    # Obtener la hora actual de Colombia (GMT-5, sin horario de verano)
    colombia_tz = timezone(timedelta(hours=-5))
    fecha_actual = datetime.now(colombia_tz)
    
    conn = get_connection()
    cur = conn.cursor()
    # Guardar la fecha con información de zona horaria
    cur.execute("INSERT INTO registros_peso (fecha_hora, peso_g) VALUES (%s, %s)", (fecha_actual, peso))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Dato insertado correctamente"}), 201

@app.route('/api/registros', methods=['GET'])
def obtener_registros():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT fecha_hora, peso_g FROM registros_peso ORDER BY id DESC LIMIT 10")
    datos = cur.fetchall()
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

@app.route('/api/indicadores', methods=['GET'])
def indicadores_reduccion():
    """Calcula indicadores simples de reducción con base en los registros.
    - baseline: primer valor registrado (g)
    - actual: último valor registrado (g)
    - reduccion_g: baseline - actual (no negativo)
    - reduccion_pct: porcentaje respecto al baseline
    - co2_kg_ev: conversión simple de residuos evitados a kgCO2e
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT peso_g FROM registros_peso ORDER BY id ASC")
    rows = cur.fetchall()
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
    app.run(debug=True)
