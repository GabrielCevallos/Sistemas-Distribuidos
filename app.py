"""
Aplicación Flask para visualizar y ejecutar ejercicios de Sistemas Distribuidos
"""

from flask import Flask, render_template, jsonify, request
import threading
import subprocess
import sys
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Variables globales para almacenar resultados
resultados_ejecucion = {
    'mutex': None,
    'semaforos': None,
    'productor_consumidor': None,
    'lector_escritor': None,
    'barrera': None
}

ejecucion_activa = {
    'status': 'idle',
    'ejercicio': None,
    'mensaje': ''
}

# Ruta del directorio de ejercicios
EJERCICIOS_DIR = os.path.dirname(os.path.abspath(__file__))


def ejecutar_ejercicio(nombre_ejercicio):
    """Ejecuta un ejercicio en un hilo separado"""
    global ejecucion_activa, resultados_ejecucion
    
    ejecucion_activa['status'] = 'running'
    ejecucion_activa['ejercicio'] = nombre_ejercicio
    ejecucion_activa['mensaje'] = f'Ejecutando {nombre_ejercicio}...'
    
    try:
        archivo_ejercicio = {
            'mutex': 'mutex.py',
            'semaforos': 'semaforos.py',
            'productor_consumidor': 'productor_consumidor.py',
            'lector_escritor': 'lector_escritor.py',
            'barrera': 'barrera.py'
        }.get(nombre_ejercicio)
        
        if not archivo_ejercicio:
            raise ValueError(f"Ejercicio desconocido: {nombre_ejercicio}")
        
        ruta_archivo = os.path.join(EJERCICIOS_DIR, archivo_ejercicio)
        
        # Ejecutar el script
        resultado = subprocess.run(
            [sys.executable, ruta_archivo],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        resultados_ejecucion[nombre_ejercicio] = {
            'timestamp': datetime.now().isoformat(),
            'stdout': resultado.stdout,
            'stderr': resultado.stderr,
            'returncode': resultado.returncode,
            'exito': resultado.returncode == 0
        }
        
        ejecucion_activa['mensaje'] = f'{nombre_ejercicio} completado'
        ejecucion_activa['status'] = 'completed'
        
    except subprocess.TimeoutExpired:
        resultados_ejecucion[nombre_ejercicio] = {
            'timestamp': datetime.now().isoformat(),
            'error': 'Timeout: ejercicio tardó demasiado',
            'exito': False
        }
        ejecucion_activa['mensaje'] = f'{nombre_ejercicio} timeout'
        ejecucion_activa['status'] = 'error'
    except Exception as e:
        resultados_ejecucion[nombre_ejercicio] = {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'exito': False
        }
        ejecucion_activa['mensaje'] = f'Error en {nombre_ejercicio}: {str(e)}'
        ejecucion_activa['status'] = 'error'


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/ejercicios', methods=['GET'])
def get_ejercicios():
    """Obtiene lista de ejercicios disponibles"""
    ejercicios = [
        {
            'id': 'mutex',
            'nombre': 'Mutex Counter'
        },
        {
            'id': 'semaforos',
            'nombre': 'Control de Gimnasio'
        },
        {
            'id': 'productor_consumidor',
            'nombre': 'Productor-Consumidor'
        },
        {
            'id': 'lector_escritor',
            'nombre': 'Lector-Escritor'
        },
        {
            'id': 'barrera',
            'nombre': 'Barrera'
        }
    ]
    return jsonify(ejercicios)


@app.route('/api/ejecutar/<ejercicio>', methods=['POST'])
def ejecutar(ejercicio):
    """Ejecuta un ejercicio específico"""
    global ejecucion_activa
    
    if ejecucion_activa['status'] == 'running':
        return jsonify({
            'error': 'Ya hay un ejercicio en ejecución',
            'status': 'error'
        }), 400
    
    # Resetear el estado antes de ejecutar
    ejecucion_activa['status'] = 'running'
    ejecucion_activa['ejercicio'] = ejercicio
    ejecucion_activa['mensaje'] = f'Iniciando {ejercicio}...'
    
    # Ejecutar en un hilo separado
    hilo = threading.Thread(target=ejecutar_ejercicio, args=(ejercicio,))
    hilo.daemon = True
    hilo.start()
    
    return jsonify({
        'mensaje': f'Iniciando {ejercicio}...',
        'status': 'started'
    })


@app.route('/api/status', methods=['GET'])
def status():
    """Obtiene el estado actual de ejecución"""
    global ejecucion_activa
    
    response = {
        'status': ejecucion_activa['status'],
        'ejercicio': ejecucion_activa['ejercicio'],
        'mensaje': ejecucion_activa['mensaje']
    }
    
    return jsonify(response)


@app.route('/api/resultados/<ejercicio>', methods=['GET'])
def get_resultados(ejercicio):
    """Obtiene los resultados de un ejercicio"""
    global resultados_ejecucion, ejecucion_activa
    
    if ejercicio not in resultados_ejecucion or resultados_ejecucion[ejercicio] is None:
        return jsonify({
            'error': f'No hay resultados para {ejercicio}',
            'status': 'error'
        }), 404
    
    resultado = resultados_ejecucion[ejercicio]
    
    # Resetear status a idle después de obtener resultados
    if ejecucion_activa['ejercicio'] == ejercicio:
        ejecucion_activa['status'] = 'idle'
        ejecucion_activa['ejercicio'] = None
        ejecucion_activa['mensaje'] = ''
    
    return jsonify(resultado)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("APLICACIÓN FLASK - SISTEMAS DISTRIBUIDOS")
    print("="*70)
    print("Acceder a: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
