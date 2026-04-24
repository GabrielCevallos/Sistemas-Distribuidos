import threading
import time
import random
from collections import deque

N_PRODUCTORES = 2
N_CONSUMIDORES = 3
ITEMS_POR_PRODUCTOR = 10
TAMANIO_BUFFER = 5
EJECUCIONES = 1


class Panaderia:
    """Implementa patrón productor-consumidor con buffer compartido"""
    
    def __init__(self, tamanio_buffer, num_productores):
        self.tamanio_buffer = tamanio_buffer
        self.buffer = deque()
        
        self.mutex = threading.Lock()
        self.condicion = threading.Condition(self.mutex)
        
        self.productores_activos = num_productores
        
        # Estadísticas
        self.items_producidos = 0
        self.items_consumidos = 0
        self.log = []
    
    def registrar(self, mensaje):
        """Registra un evento"""
        print(mensaje)
        self.log.append(mensaje)
    
    def producir(self, id_productor, id_item):
        """Inserta item en el buffer si hay espacio"""
        with self.condicion:
            while len(self.buffer) >= self.tamanio_buffer:
                self.registrar(f"  [PRODUCTOR {id_productor}] Esperando espacio (buffer={len(self.buffer)}/{self.tamanio_buffer})")
                self.condicion.wait()
            
            self.buffer.append(id_item)
            self.registrar(f"  [PRODUCTOR {id_productor}] Insertó item {id_item} (buffer={list(self.buffer)})")
            
            self.items_producidos += 1
            self.condicion.notify_all()
    
    def consumir(self, id_consumidor):
        """Extrae item del buffer si está disponible"""
        with self.condicion:
            while len(self.buffer) == 0 and self.productores_activos > 0:
                self.registrar(f"  [CONSUMIDOR {id_consumidor}] Esperando items...")
                self.condicion.wait()
            
            if len(self.buffer) == 0:
                return None
            
            item = self.buffer.popleft()
            self.registrar(f"  [CONSUMIDOR {id_consumidor}] Consumió item {item} (buffer={list(self.buffer)})")
            
            self.items_consumidos += 1
            self.condicion.notify_all()
            return item
    
    def marcar_productor_finalizado(self):
        """Marca que un productor ha terminado"""
        with self.condicion:
            self.productores_activos -= 1
            self.registrar(f"  [COORDINADOR] Productor terminó (activos={self.productores_activos})")
            self.condicion.notify_all()


def ejecutar_productor(id_productor, panaderia, num_items):
    """Función ejecutada por cada productor"""
    for i in range(1, num_items + 1):
        id_item = f"P{id_productor}-I{i}"
        print(f"[PRODUCTOR {id_productor}] Hornea item {id_item}")
        
        # Simular tiempo de preparación
        tiempo_prep = random.uniform(0.05, 0.15)
        time.sleep(tiempo_prep)
        
        panaderia.producir(id_productor, id_item)
    
    panaderia.marcar_productor_finalizado()
    print(f"[PRODUCTOR {id_productor}] FINALIZADO")


def ejecutar_consumidor(id_consumidor, panaderia):
    """Función ejecutada por cada consumidor"""
    items_consumidos_locales = 0
    
    while True:
        item = panaderia.consumir(id_consumidor)
        if item is None:
            break
        items_consumidos_locales += 1
        
        # Simular consumo
        tiempo_consumo = random.uniform(0.05, 0.15)
        time.sleep(tiempo_consumo)
    
    print(f"[CONSUMIDOR {id_consumidor}] FINALIZADO (consumidos: {items_consumidos_locales})")


def ejecutar_simulacion_productor_consumidor(numero_ejecucion):
    """Ejecuta una simulación completa de Productor-Consumidor"""
    print(f"\n[EJECUCION {numero_ejecucion}] {N_PRODUCTORES} productores, {N_CONSUMIDORES} consumidores")
    
    panaderia = Panaderia(TAMANIO_BUFFER, N_PRODUCTORES)
    hilos = []
    
    inicio = time.perf_counter()
    
    # Crear productores
    total_items = N_PRODUCTORES * ITEMS_POR_PRODUCTOR
    
    for i in range(1, N_PRODUCTORES + 1):
        hilo = threading.Thread(target=ejecutar_productor, args=(i, panaderia, ITEMS_POR_PRODUCTOR))
        hilos.append(hilo)
        hilo.start()
    
    # Crear consumidores
    for i in range(1, N_CONSUMIDORES + 1):
        hilo = threading.Thread(target=ejecutar_consumidor, args=(i, panaderia))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que terminen todos
    for hilo in hilos:
        hilo.join()
    
    fin = time.perf_counter()
    
    es_valido = panaderia.items_producidos == panaderia.items_consumidos == total_items
    estado = "VALIDO" if es_valido else "INVALIDO"
    
    print(f"\n[VALIDACION EJECUCION {numero_ejecucion}]")
    print(f"  Items totales esperados: {total_items}")
    print(f"  Items producidos: {panaderia.items_producidos}")
    print(f"  Items consumidos: {panaderia.items_consumidos}")
    print(f"  Resultado: {estado}")
    print(f"  Tiempo total: {(fin - inicio) * 1000:.3f}ms")
    print(f"  Buffer final: {list(panaderia.buffer)}")
    
    return es_valido


def main():
    print("\nEJERCICIO 3: PRODUCTOR-CONSUMIDOR")

    print(f"Total de ejecuciones: {EJECUCIONES}\n")
    
    resultados = []
    
    for i in range(1, EJECUCIONES + 1):
        valido = ejecutar_simulacion_productor_consumidor(i)
        resultados.append(valido)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
