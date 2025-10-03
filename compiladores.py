import threading
import time
import random
import collections
from datetime import datetime

class GerenciadorRecursos:
    def __init__(self):
        self.compilador_em_uso = False
        self.bd_em_uso = 0
        self.capacidade_bd = 2
        self.cond = threading.Condition()
        self.fila = collections.deque()

    def pedir_recursos(self, id_prog):
        with self.cond:
            self.fila.append(id_prog)
            while not (self.fila[0] == id_prog and not self.compilador_em_uso and self.bd_em_uso < self.capacidade_bd):
                self.cond.wait()
            self.compilador_em_uso = True
            self.bd_em_uso += 1
            self.fila.popleft()

    def liberar_recursos(self):
        with self.cond:
            self.compilador_em_uso = False
            self.bd_em_uso -= 1
            self.cond.notify_all()

status_lock = threading.Lock()
estados = {}

def definir_estado(id_prog, texto):
    with status_lock:
        estados[id_prog] = texto

def imprimir(msg):
    print(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")

def programador(id_prog, gerenciador):
    while True:
        definir_estado(id_prog, "Pensando")
        imprimir(f"Programador {id_prog}: Pensando/descansando.")
        time.sleep(random.uniform(10, 15))

        definir_estado(id_prog, "Esperando recursos")
        imprimir(f"Programador {id_prog}: Vai pedir compilador + BD (fila).")
        gerenciador.pedir_recursos(id_prog)

        definir_estado(id_prog, "Compilando")
        imprimir(f"Programador {id_prog}: RECEBEU compilador + BD -> Compilando.")
        time.sleep(random.uniform(12, 18))

        imprimir(f"Programador {id_prog}: Terminou compilação. Liberando recursos.")
        gerenciador.liberar_recursos()

        time.sleep(random.uniform(3, 5))

ultimo_snapshot = None
def monitorar(periodo=6):
    global ultimo_snapshot
    while True:
        with status_lock:
            snapshot = " | ".join(f"{pid}:{estado}" for pid, estado in sorted(estados.items()))
        if snapshot != ultimo_snapshot:
            imprimir("STATUS -> " + snapshot)
            ultimo_snapshot = snapshot
        time.sleep(periodo)

def main():
    num_programadores = 5
    gerenciador = GerenciadorRecursos()
    threads = []
    for pid in range(1, num_programadores + 1):
        definir_estado(pid, "Inicializando")
        t = threading.Thread(target=programador, args=(pid, gerenciador), daemon=True)
        t.start()
        threads.append(t)

    mon = threading.Thread(target=monitorar, args=(6.0,), daemon=True)
    mon.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        imprimir("Encerramento solicitado pelo usuário (Ctrl+C).")

if __name__ == "__main__":
    main()
