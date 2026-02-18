#  Menos Residuos, Más Conciencia

Una aplicación web moderna desarrollada con Flask para el registro y seguimiento de la reducción de residuos, con el objetivo de promover la conciencia ambiental y medir el impacto positivo en la reducción de emisiones de CO₂.

##  Descripción

Esta plataforma permite registrar y monitorear el peso de residuos generados, calcular indicadores de reducción y visualizar estadísticas en tiempo real. La aplicación está diseñada para ayudar a individuos y organizaciones a:

-  Registrar pesos de residuos de manera sencilla
-  Visualizar estadísticas y tendencias
-  Calcular el impacto ambiental (CO₂ evitado)
-  Acceder desde cualquier dispositivo con una interfaz responsive

##  Características

- **Registro de Pesos**: Formulario intuitivo para registrar pesos en gramos
- **Dashboard de Indicadores**: Visualización de totales, promedios, mínimos y máximos
- **Historial de Registros**: Tabla con los últimos registros ordenados por fecha
- **Cálculo de CO₂**: Conversión automática de residuos evitados a kg de CO₂ equivalente
- **Zona Horaria**: Configurado para hora de Colombia (GMT-5)
- **Interfaz Moderna**: Diseño oscuro y responsive con animaciones suaves
- **Actualización en Tiempo Real**: Los datos se actualizan sin recargar la página

##  Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos**: PostgreSQL (Neon)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Iconos**: Font Awesome
- **Variables de Entorno**: python-dotenv

##  Requisitos Previos

- Python 3.8 o superior
- PostgreSQL (o acceso a una base de datos PostgreSQL)
- pip (gestor de paquetes de Python)

##  Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/AndreRivas1103/ProyectodeIngenieria
cd ProyectodeIngenieria
```

### 2. Crear un entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```


### 5. Crear la tabla en la base de datos

Ejecuta el siguiente SQL en tu base de datos PostgreSQL:

```sql
CREATE TABLE IF NOT EXISTS registros_peso (
    id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP WITH TIME ZONE NOT NULL,
    peso_g DECIMAL(10, 2) NOT NULL
);
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

##  Uso

### Registrar un nuevo peso

1. Ingresa al formulario "Registrar Nuevo Peso"
2. Ingresa el peso en gramos (ejemplo: 1500)
3. Haz clic en "Agregar Registro"
4. El registro se guardará automáticamente y la tabla se actualizará

### Ver estadísticas

- Los indicadores se muestran automáticamente en la sección "Indicadores de Registros"
- Incluye: Total, Promedio, Mínimo, Máximo, Cantidad de registros y CO₂ evitado

### Actualizar datos

- Haz clic en el botón "Actualizar" para refrescar los datos sin recargar la página

##  Seguridad

- ✅ Las credenciales de la base de datos están protegidas en variables de entorno
- ✅ Validación de datos en el servidor y cliente
- ✅ Protección contra inyección SQL mediante parámetros preparados
- ✅ El archivo `.env` está excluido del control de versiones

##  Estructura del Proyecto

```
ProyectodeIngenieria/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias de Python
├── .env                   # Variables de entorno (no se sube a git)
├── .gitignore            # Archivos excluidos de git
├── README.md             # Este archivo
├── templates/
│   └── index.html        # Plantilla HTML principal
└── src/                  # Archivos estáticos (imágenes, CSS, JS)
```


##  Autor

Proyecto de Ingeniería - Sistema de Registro de Residuos




