import threading
import time

N_HILOS = 5
FASES = 2
EJECUCIONES = 1


class Barrera:
    """Implementa barrera de sincronización con generaciones"""
    
    def __init__(self, n_total):
        self.n_total = n_total
        self.contador = 0
        self.generacion = 0
        self.mutex = threading.Lock()
        self.var_cond = threading.Condition(self.mutex)
        self.log = []
    
    def registrar(self, mensaje):
        """Registra un evento"""
        print(mensaje)
        self.log.append(mensaje)
    
    def esperar(self, id_hilo, fase):
        """Sincroniza hilos en punto de control"""
        with self.var_cond:
            mi_generacion = self.generacion
            self.contador += 1
            self.registrar(f"  [HILO {id_hilo}] Fase {fase}: LLEGÓ (contador={self.contador}/{self.n_total})")
            
            if self.contador == self.n_total:
                self.registrar(f"  [HILO {id_hilo}] Fase {fase}: Último hilo - notifica a todos")
                self.generacion += 1
                self.contador = 0
                self.var_cond.notify_all()
            else:
                self.registrar(f"  [HILO {id_hilo}] Fase {fase}: Esperando a otros hilos...")
                
                while mi_generacion == self.generacion:
                    self.var_cond.wait()
                
                self.registrar(f"  [HILO {id_hilo}] Fase {fase}: Despertó - puede continuar")


def ejecutar_hilo(id_hilo, barrera):
    """Ejecuta múltiples fases con sincronización en barrera"""
    for fase in range(1, FASES + 1):
        print(f"[HILO {id_hilo}] FASE {fase} INICIADA")
        barrera.esperar(id_hilo, fase)
        print(f"[HILO {id_hilo}] FASE {fase} COMPLETADA")
        time.sleep(0.2)


def ejecutar_simulacion_barrera(numero_ejecucion):
    """Ejecuta una simulación completa de Barrera"""
    print(f"\n[EJECUCION {numero_ejecucion}] {N_HILOS} hilos, {FASES} fases")
    
    barrera = Barrera(N_HILOS)
    hilos = []
    
    inicio = time.perf_counter()
    
    # Crear hilos
    for i in range(1, N_HILOS + 1):
        hilo = threading.Thread(target=ejecutar_hilo, args=(i, barrera))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que terminen todos
    for hilo in hilos:
        hilo.join()
    
    fin = time.perf_counter()
    
    es_valido = True
    
    print(f"Tiempo total: {(fin - inicio) * 1000:.3f}ms")
    
    return es_valido


def main():
    print("\nEJERCICIO 5: BARRERA DE SINCRONIZACION")
    print(f"Total de ejecuciones: {EJECUCIONES}\n")
    
    resultados = []
    
    for i in range(1, EJECUCIONES + 1):
        valido = ejecutar_simulacion_barrera(i)
        resultados.append(valido)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
