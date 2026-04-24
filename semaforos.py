import threading
import time
import random

N_ATLETAS = 10
TIEMPO_USO_MIN = 0.5
TIEMPO_USO_MAX = 2.0
EJECUCIONES = 1
RECURSOS_DISPONIBLES = 3


class MiSemaforo:
    """Implementa semáforo con contador compartido protegido"""
    
    def __init__(self, valor_inicial):
        self.contador = valor_inicial
        self.mutex = threading.Lock()
        self.condicion = threading.Condition(self.mutex)
    
    def esperar(self):
        """Decrementa el contador, espera si es necesario"""
        with self.condicion:
            while self.contador == 0:
                print(f"  [SEMAFORO] Hilo bloqueado - esperando recurso (contador={self.contador})")
                self.condicion.wait()
            self.contador -= 1
    
    def senial(self):
        """Incrementa el contador y notifica a hilos en espera"""
        with self.condicion:
            self.contador += 1
            self.condicion.notify()


class ControlGimnasio:
    """Simula el control de acceso a máquinas de gimnasio"""
    
    def __init__(self, num_recursos):
        self.semaforo = MiSemaforo(num_recursos)
        self.resources_in_use = 0
        self.resources_max = 0
        self.mutex_stats = threading.Lock()
    
    def usar_maquina(self, id_atleta):
        """Adquiere recurso, lo usa y lo libera"""
        print(f"[ATLETA {id_atleta}] Intenta acceder a máquina")
        
        self.semaforo.esperar()
        
        with self.mutex_stats:
            self.resources_in_use += 1
            if self.resources_in_use > self.resources_max:
                self.resources_max = self.resources_in_use
            print(f"[ATLETA {id_atleta}] Adquirió máquina (en_uso={self.resources_in_use})")
        
        tiempo_uso = random.uniform(TIEMPO_USO_MIN, TIEMPO_USO_MAX)
        time.sleep(tiempo_uso)
        
        with self.mutex_stats:
            self.resources_in_use -= 1
            print(f"[ATLETA {id_atleta}] Liberó máquina (en_uso={self.resources_in_use})")
        
        self.semaforo.senial()
        print(f"[ATLETA {id_atleta}] Finalizó")


def ejecutar_simulacion_gimnasio(numero_ejecucion):
    """Ejecuta una simulación completa del gimnasio"""
    print(f"\n[EJECUCION {numero_ejecucion}] {N_ATLETAS} atletas, {RECURSOS_DISPONIBLES} máquinas")
    
    gimnasio = ControlGimnasio(RECURSOS_DISPONIBLES)
    hilos = []
    
    inicio = time.perf_counter()
    
    for i in range(1, N_ATLETAS + 1):
        hilo = threading.Thread(target=gimnasio.usar_maquina, args=(i,))
        hilos.append(hilo)
        hilo.start()
    
    for hilo in hilos:
        hilo.join()
    
    fin = time.perf_counter()
    
    es_valido = gimnasio.resources_max <= RECURSOS_DISPONIBLES
    
    print(f"Tiempo total: {(fin - inicio) * 1000:.3f}ms")
    
    return es_valido, gimnasio.resources_max


def main():
    print("\nEJERCICIO 2: CONTROL DE GIMNASIO CON SEMÁFOROS")

    print(f"Total de ejecuciones: {EJECUCIONES}\n")
    
    resultados = []
    maximos = []
    
    for i in range(1, EJECUCIONES + 1):
        valido, maximo = ejecutar_simulacion_gimnasio(i)
        resultados.append(valido)
        maximos.append(maximo)


if __name__ == "__main__":
    main()
