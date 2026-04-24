import threading
import time
import random

N_LECTORES = 5
N_ESCRITORES = 2
OPERACIONES_POR_LECTOR = 3
OPERACIONES_POR_ESCRITOR = 2
EJECUCIONES = 1


class TabloNotasRWLock:
    """Implementa patrón lector-escritor con control de acceso"""
    
    def __init__(self):
        self.cant_lectores = 0
        self.mutex_lectores = threading.Lock()
        self.sem_escritor = threading.Semaphore(1)
        self.valor_tablon = 0
        
        # Estadísticas
        self.log = []
    
    def registrar(self, mensaje):
        """Registra un evento"""
        print(mensaje)
        self.log.append(mensaje)
    
    def entrar_lector(self, id_lector):
        """Incrementa contador de lectores y bloquea escritores si necesario"""
        with self.mutex_lectores:
            self.cant_lectores += 1
            self.registrar(f"  [LECTOR {id_lector}] ENTRA (cant_lectores={self.cant_lectores})")
            
            if self.cant_lectores == 1:
                self.registrar(f"  [LECTOR {id_lector}] Primer lector: bloquea escritores")
                self.sem_escritor.acquire()
    
    def salir_lector(self, id_lector):
        """Decrementa contador de lectores y desbloquea escritores si es necesario"""
        with self.mutex_lectores:
            self.cant_lectores -= 1
            self.registrar(f"  [LECTOR {id_lector}] SALE (cant_lectores={self.cant_lectores})")
            
            if self.cant_lectores == 0:
                self.registrar(f"  [LECTOR {id_lector}] Último lector: desbloquea escritores")
                self.sem_escritor.release()
    
    def leer(self, id_lector):
        """Ejecuta operación de lectura"""
        self.entrar_lector(id_lector)
        
        self.registrar(f"  [LECTOR {id_lector}] LEE tablón (valor={self.valor_tablon})")
        tiempo_lectura = random.uniform(0.1, 0.3)
        time.sleep(tiempo_lectura)
        
        self.salir_lector(id_lector)
    
    def escribir(self, id_escritor, nuevo_valor):
        """Ejecuta operación de escritura con acceso exclusivo"""
        self.registrar(f"  [ESCRITOR {id_escritor}] Intenta acceso exclusivo")
        self.sem_escritor.acquire()
        self.registrar(f"  [ESCRITOR {id_escritor}] Adquiere acceso exclusivo")
        
        self.valor_tablon = nuevo_valor
        self.registrar(f"  [ESCRITOR {id_escritor}] ESCRIBE tablón (valor={nuevo_valor})")
        tiempo_escritura = random.uniform(0.2, 0.5)
        time.sleep(tiempo_escritura)
        
        self.sem_escritor.release()
        self.registrar(f"  [ESCRITOR {id_escritor}] Libera acceso exclusivo")


def ejecutar_lector(id_lector, tablon, num_operaciones):
    """Función ejecutada por cada lector"""
    for i in range(1, num_operaciones + 1):
        print(f"[LECTOR {id_lector}] Operación {i}/{num_operaciones}")
        tablon.leer(id_lector)
        time.sleep(random.uniform(0.1, 0.2))


def ejecutar_escritor(id_escritor, tablon, num_operaciones):
    """Función ejecutada por cada escritor"""
    for i in range(1, num_operaciones + 1):
        print(f"[ESCRITOR {id_escritor}] Operación {i}/{num_operaciones}")
        nuevo_valor = id_escritor * 100 + i
        tablon.escribir(id_escritor, nuevo_valor)
        time.sleep(random.uniform(0.1, 0.2))


def verificar_patron_acceso(log):
    """Verifica que el patrón de acceso sea correcto"""
    # El patrón debe mostrar:
    # - Múltiples lectores leyendo simultáneamente
    # - Escritores nunca superponiéndose
    # - Transiciones correctas
    
    en_lectura = []
    en_escritura = False
    eventos_validos = True
    
    for evento in log:
        if "LECTOR" in evento and "LEE tablón" in evento:
            # Extraer ID del lector
            import re
            match = re.search(r'LECTOR (\d+)', evento)
            if match:
                lector_id = match.group(1)
                en_lectura.append(lector_id)
        
        elif "ESCRITOR" in evento and "ESCRIBE tablón" in evento:
            # Un escritor está escribiendo
            import re
            match = re.search(r'ESCRITOR (\d+)', evento)
            if match:
                if en_lectura:  # Error: escritor y lectores simultáneos
                    eventos_validos = False
                en_escritura = True
        
        elif "LECTOR" in evento and "SALE" in evento:
            # Extraer ID del lector
            import re
            match = re.search(r'LECTOR (\d+)', evento)
            if match:
                lector_id = match.group(1)
                if lector_id in en_lectura:
                    en_lectura.remove(lector_id)
    
    return eventos_validos and len(en_lectura) == 0


def ejecutar_simulacion_lector_escritor(numero_ejecucion):
    """Ejecuta una simulación completa de Lector-Escritor"""
    print(f"\n[EJECUCION {numero_ejecucion}] {N_LECTORES} lectores, {N_ESCRITORES} escritores")
    
    tablon = TabloNotasRWLock()
    hilos = []
    
    inicio = time.perf_counter()
    
    # Crear lectores
    for i in range(1, N_LECTORES + 1):
        hilo = threading.Thread(target=ejecutar_lector, args=(i, tablon, OPERACIONES_POR_LECTOR))
        hilos.append(hilo)
        hilo.start()
    
    # Crear escritores
    for i in range(1, N_ESCRITORES + 1):
        hilo = threading.Thread(target=ejecutar_escritor, args=(i, tablon, OPERACIONES_POR_ESCRITOR))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que terminen todos
    for hilo in hilos:
        hilo.join()
    
    fin = time.perf_counter()
    
    # Validación: verificar patrón de acceso
    patron_valido = verificar_patron_acceso(tablon.log)
    estado = "VALIDO" if patron_valido else "INVALIDO"
    
    print(f"\n[VALIDACION EJECUCION {numero_ejecucion}]")
    print(f"  Patrón de acceso correcto: [{estado}]")
    print(f"  Valor final del tablón: {tablon.valor_tablon}")
    print(f"  Tiempo total: {(fin - inicio) * 1000:.3f}ms")
    print(f"  Total eventos: {len(tablon.log)}")
    
    return patron_valido


def main():
    print("\nEJERCICIO 4: LECTOR-ESCRITOR")

    print(f"Total de ejecuciones: {EJECUCIONES}\n")
    
    resultados = []
    
    for i in range(1, EJECUCIONES + 1):
        valido = ejecutar_simulacion_lector_escritor(i)
        resultados.append(valido)
        time.sleep(0.5)



if __name__ == "__main__":
    main()
