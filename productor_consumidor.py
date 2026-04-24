import threading
import time
import random
from collections import deque

N_PRODUCTORES = 2
N_CONSUMIDORES = 3
ITEMS_POR_PRODUCTOR = 10
TAMANIO_BUFFER = 10
EJECUCIONES = 1


class Vitrina:
    """Implementa patrón productor-consumidor con buffer compartido"""
    
    def __init__(self, tamanio_buffer, num_productores):
        self.tamanio_buffer = tamanio_buffer
        self.buffer = deque()
        
        self.mutex = threading.Lock()
        self.condicion = threading.Condition(self.mutex)
        
        self.productores_activos = num_productores
        
        # Estadísticas
        self.contador_panes = 0
        self.items_producidos = 0
        self.items_consumidos = 0
    
    def producir(self, id_productor):
        """Inserta pan en la vitrina si hay espacio"""
        with self.condicion:
            while len(self.buffer) >= self.tamanio_buffer:
                self.condicion.wait()
            
            self.contador_panes += 1
            pan_id = self.contador_panes
            self.buffer.append(pan_id)
            print(f"Panadero: horneó Pan#{pan_id}")
            print(f"Panadero: puso Pan#{pan_id} en vitrina (vitrina={len(self.buffer)})")
            
            self.items_producidos += 1
            self.condicion.notify_all()
    
    def consumir(self, id_consumidor):
        """Extrae pan de la vitrina si está disponible"""
        with self.condicion:
            while len(self.buffer) == 0 and self.productores_activos > 0:
                self.condicion.wait()
            
            if len(self.buffer) == 0:
                return None
            
            pan_id = self.buffer.popleft()
            print(f"Cliente: tomó Pan#{pan_id} de vitrina (vitrina={len(self.buffer)})")
            
            self.items_consumidos += 1
            self.condicion.notify_all()
            return pan_id
    
    def marcar_productor_finalizado(self):
        """Marca que un productor ha terminado"""
        with self.condicion:
            self.productores_activos -= 1
            self.condicion.notify_all()


def ejecutar_productor(id_productor, vitrina, num_items):
    """Función ejecutada por cada productor"""
    for i in range(1, num_items + 1):
        # Simular tiempo de preparación
        tiempo_prep = random.uniform(0.02, 0.05)
        time.sleep(tiempo_prep)
        
        vitrina.producir(id_productor)
    
    vitrina.marcar_productor_finalizado()


def ejecutar_consumidor(id_consumidor, vitrina):
    """Función ejecutada por cada consumidor"""
    while True:
        # Simular tiempo de consumo
        tiempo_consumo = random.uniform(0.02, 0.05)
        time.sleep(tiempo_consumo)
        
        item = vitrina.consumir(id_consumidor)
        if item is None:
            break


def ejecutar_simulacion_productor_consumidor(numero_ejecucion):
    """Ejecuta una simulación completa de Productor-Consumidor"""
    total_items = N_PRODUCTORES * ITEMS_POR_PRODUCTOR
    
    print(f"\n[Prod-Cons] Vitrina cap={TAMANIO_BUFFER}, produciendo {total_items} panes...")
    
    vitrina = Vitrina(TAMANIO_BUFFER, N_PRODUCTORES)
    hilos = []
    
    inicio = time.perf_counter()
    
    # Crear productores
    for i in range(1, N_PRODUCTORES + 1):
        hilo = threading.Thread(target=ejecutar_productor, args=(i, vitrina, ITEMS_POR_PRODUCTOR))
        hilos.append(hilo)
        hilo.start()
    
    # Crear consumidores
    for i in range(1, N_CONSUMIDORES + 1):
        hilo = threading.Thread(target=ejecutar_consumidor, args=(i, vitrina))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que terminen todos
    for hilo in hilos:
        hilo.join()
    
    fin = time.perf_counter()
    tiempo_ms = (fin - inicio) * 1000
    
    es_valido = vitrina.items_producidos == vitrina.items_consumidos == total_items
    
    print(f"Panes producidos   : {vitrina.items_producidos}")
    print(f"Panes consumidos   : {vitrina.items_consumidos}")
    print(f"Todos consumidos   : {'CORRECTO' if es_valido else 'INCORRECTO'}")
    print(f"Vitrina al final   : {len(vitrina.buffer)} items")
    print(f"Tiempo total       : {tiempo_ms:.2f}ms\n")
    
    return es_valido


def main():
    resultados = []
    
    for i in range(1, EJECUCIONES + 1):
        valido = ejecutar_simulacion_productor_consumidor(i)
        resultados.append(valido)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
