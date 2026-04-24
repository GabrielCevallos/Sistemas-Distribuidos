import threading
import time

N_HILOS = 5
M_VENTAS = 1_000_000
TOTAL_ESPERADO = N_HILOS * M_VENTAS
EJECUCIONES = 10


def venta_secuencial():
    """Ejecuta ventas de forma secuencial para comparación"""
    inicio = time.perf_counter()
    total = 0
    for _ in range(TOTAL_ESPERADO):
        total += 1
    fin = time.perf_counter()

    print("\n[SECUENCIAL] Ejecución de referencia:")
    print(f"  Total vendido: {total}")
    print(f"  Tiempo total: {(fin - inicio) * 1000:.6f}ms")
    validacion = "CORRECTO" if total == TOTAL_ESPERADO else "INCORRECTO"
    print(f"  Validación: {validacion}")
    return fin - inicio


def ejecutar_venta(id_tarea, compartido, mutex):
    """Ejecuta operaciones de venta protegidas por mutex"""
    print(f"[INICIO] Tarea {id_tarea}: inicia venta ({M_VENTAS} boletos)")
    ventas_locales = 0

    for _ in range(M_VENTAS):
        with mutex:
            compartido["boletos_vendidos"] += 1
        ventas_locales += 1

    print(f"[FIN] Tarea {id_tarea}: finaliza - vendidos: {ventas_locales}")


def una_ejecucion(numero):
    """Ejecuta una simulación completa de venta atómica"""
    compartido = {"boletos_vendidos": 0}
    mutex = threading.Lock()
    hilos = []

    inicio = time.perf_counter()

    for i in range(1, N_HILOS + 1):
        hilo = threading.Thread(target=ejecutar_venta, args=(i, compartido, mutex))
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    fin = time.perf_counter()
    total = compartido["boletos_vendidos"]
    estado = "CORRECTO" if total == TOTAL_ESPERADO else "INCORRECTO"
    
    print(f"[EJECUCION {numero}] Total: {total}, Tiempo: {(fin - inicio) * 1000:.6f}ms, {estado}")
    return total, fin - inicio


def main():
    print("\nEJERCICIO 1: MUTEX COUNTER (VENTA ATOMICA)")

    print(f"Parámetros: {N_HILOS} hilos, {M_VENTAS:,} operaciones, {EJECUCIONES} ejecuciones\n")
    
    tiempo_sec = venta_secuencial()

    print("\nEjecutando con Mutex:")

    resultados = []
    tiempos = []
    
    for i in range(1, EJECUCIONES + 1):
        total, tiempo = una_ejecucion(i)
        resultados.append(total)
        tiempos.append(tiempo)

    correctas = sum(1 for r in resultados if r == TOTAL_ESPERADO)
    todas_correctas = correctas == EJECUCIONES

    tiempo_promedio = (sum(tiempos) / len(tiempos)) * 1000
    print(f"Tiempo promedio: {tiempo_promedio:.2f}ms")


if __name__ == "__main__":
    main()