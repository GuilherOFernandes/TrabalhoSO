import json
import random
import math
import pandas as pd
from collections import deque

# Conexão do JSON com o código
workload_json_content = """
{
  "spec_version": "1.0",
  "challenge_id": "os_rr_fcfs_sjf_demo_manual_1",
  "metadata": {
    "context_switch_cost": 1,
    "throughput_window_T": 20,
    "algorithms": ["FCFS", "SJF", "RR"],
    "rr_quantums": [2, 4, 8]
  },
  "workload": {
    "time_unit": "ticks",
    "processes": [
      { "pid": "P01", "arrival_time": 0,  "burst_time": 6 },
      { "pid": "P02", "arrival_time": 1,  "burst_time": 3 },
      { "pid": "P03", "arrival_time": 2,  "burst_time": 8 },
      { "pid": "P04", "arrival_time": 4,  "burst_time": 4 },
      { "pid": "P05", "arrival_time": 6,  "burst_time": 5 }
    ]
  }
}
"""
# Processo 

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.completion_time = -1
        self.turnaround_time = -1
        self.waiting_time = -1
        self.start_time = -1

# Calcular métricas 
def calculate_metrics(processes, throughput_window):
    completed_processes = [p for p in processes if p.completion_time != -1]
    
    if not completed_processes:
        return {
            'vazao': 0.0,
            'tempo_medio_retorno': 0.0,
            'std_retorno': 0.0,
            'tempo_medio_espera': 0.0,
            'std_espera': 0.0
        }

    # Calcular tempo de retorno e espera para cada processo

    turnaround_times = []
    waiting_times = []
    for p in completed_processes:
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        turnaround_times.append(p.turnaround_time)
        waiting_times.append(p.waiting_time)

    avg_turnaround = sum(turnaround_times) / len(turnaround_times)
    avg_waiting = sum(waiting_times) / len(waiting_times)

    std_turnaround = math.sqrt(sum((t - avg_turnaround) ** 2 for t in turnaround_times) / (len(turnaround_times) - 1 if len(turnaround_times) > 1 else 1))
    std_waiting = math.sqrt(sum((w - avg_waiting) ** 2 for w in waiting_times) / (len(waiting_times) - 1 if len(waiting_times) > 1 else 1))

    completed_in_window = sum(1 for p in completed_processes if p.completion_time <= throughput_window)
    vazao = completed_in_window / throughput_window if throughput_window > 0 else 0

    return {
        'vazao': vazao,
        'tempo_medio_retorno': avg_turnaround,
        'std_retorno': std_turnaround,
        'tempo_medio_espera': avg_waiting,
        'std_espera': std_waiting
    }

# Simular o escalonamento 

def run_simulation(processes, algorithm, context_switch_cost, quantum=None):
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    completed_count = 0
    
    # Fila de prontos 
    ready_queue = deque()
    in_ready_queue = set()

    processes_map = {p.pid: p for p in processes}
    execution_sequence = []

    if algorithm == "FCFS":
        # Simula FCFS 
        current_time = processes[0].arrival_time
        
        for p in processes:
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            
            p.start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            execution_sequence.append({'pid': p.pid, 'start': p.start_time, 'end': p.completion_time})

            # Adiciona o custo de troca de contexto entre processos
            current_time += context_switch_cost

    elif algorithm == "SJF":
        # Simula SJF 
        completed_processes = 0
        current_time = 0
        processes_sorted_by_arrival = sorted(processes, key=lambda p: p.arrival_time)
        available_processes_index = 0
        
        while completed_processes < len(processes):
            # Adiciona processos que chegaram na fila de prontos
            while available_processes_index < len(processes_sorted_by_arrival) and \
                  processes_sorted_by_arrival[available_processes_index].arrival_time <= current_time:
                p = processes_sorted_by_arrival[available_processes_index]
                if p.pid not in in_ready_queue:
                    ready_queue.append(p)
                    in_ready_queue.add(p.pid)
                available_processes_index += 1
            
            if not ready_queue:
                if available_processes_index < len(processes_sorted_by_arrival):
                    current_time = processes_sorted_by_arrival[available_processes_index].arrival_time
                continue

            ready_queue = deque(sorted(list(ready_queue), key=lambda p: p.burst_time))
            p = ready_queue.popleft()
            in_ready_queue.remove(p.pid)

            p.start_time = current_time
            current_time += p.burst_time
            p.completion_time = current_time
            execution_sequence.append({'pid': p.pid, 'start': p.start_time, 'end': p.completion_time})
            completed_processes += 1

            if completed_processes < len(processes):
                current_time += context_switch_cost
    
    elif algorithm == "RR":
        current_time = 0
        completed_processes = 0
        
        initial_processes = [p for p in processes if p.arrival_time <= current_time]
        initial_processes.sort(key=lambda p: p.arrival_time)
        ready_queue.extend(initial_processes)
        in_ready_queue.update(p.pid for p in initial_processes)

        last_pid = None
        
        while completed_processes < len(processes):
            
            if not ready_queue:
                next_arrival = min([p.arrival_time for p in processes if p.pid not in in_ready_queue and p.completion_time == -1], default=None)
                if next_arrival is not None:
                    current_time = max(current_time, next_arrival)
                else:
                    break

                for p in sorted(processes, key=lambda p: p.arrival_time):
                    if p.arrival_time <= current_time and p.pid not in in_ready_queue and p.completion_time == -1:
                        ready_queue.append(p)
                        in_ready_queue.add(p.pid)
                
                continue
            
            p = ready_queue.popleft()
            
            if last_pid is not None and last_pid != p.pid:
                current_time += context_switch_cost

            execution_start = current_time
            time_to_execute = min(p.remaining_time, quantum)
            current_time += time_to_execute
            p.remaining_time -= time_to_execute
            
            execution_sequence.append({'pid': p.pid, 'start': execution_start, 'end': current_time})

            for new_p in sorted(processes, key=lambda p: p.arrival_time):
                if new_p.arrival_time > execution_start and new_p.arrival_time <= current_time and new_p.pid not in in_ready_queue and new_p.completion_time == -1:
                    ready_queue.append(new_p)
                    in_ready_queue.add(new_p.pid)
            
            if p.remaining_time == 0:
                p.completion_time = current_time
                completed_processes += 1
                in_ready_queue.remove(p.pid)
            else:
                ready_queue.append(p)

            last_pid = p.pid

    return processes, execution_sequence


def generate_random_processes(num_processes, burst_range, arrival_range):
    processes = []
    for i in range(num_processes):
        pid = f"P{i:02d}"
        arrival_time = random.randint(arrival_range[0], arrival_range[1])
        burst_time = random.randint(burst_range[0], burst_range[1])
        processes.append(Process(pid, arrival_time, burst_time))
    return processes

config = json.loads(workload_json_content)
context_switch_cost = config['metadata']['context_switch_cost']
throughput_window = 20
algorithms = config['metadata']['algorithms']
rr_quantums = config['metadata']['rr_quantums']

results = []

# Executa simulações para cada algoritmo e quantum
json_processes_data = config['workload']['processes']
for algo in algorithms:
    if algo == "RR":
        for q in rr_quantums:
            sim_processes = [
                Process(p['pid'], p['arrival_time'], p['burst_time'])
                for p in json_processes_data
            ]
            final_processes, sequence = run_simulation(sim_processes, algo, context_switch_cost, q)
            metrics = calculate_metrics(final_processes, throughput_window)
            results.append({
                'Algoritmo': f'{algo} (Quantum={q})',
                'Vazão': metrics['vazao'],
                'Tempo Médio de Retorno': f"{metrics['tempo_medio_retorno']:.2f}",
                'Tempo Médio de Espera': f"{metrics['tempo_medio_espera']:.2f}",
                'Sequencia de Execucao': sequence
            })
    else:
        sim_processes = [
            Process(p['pid'], p['arrival_time'], p['burst_time'])
            for p in json_processes_data
        ]
        final_processes, sequence = run_simulation(sim_processes, algo, context_switch_cost)
        metrics = calculate_metrics(final_processes, throughput_window)
        results.append({
            'Algoritmo': algo,
            'Vazão': metrics['vazao'],
            'Tempo Médio de Retorno': f"{metrics['tempo_medio_retorno']:.2f}",
                'Tempo Médio de Espera': f"{metrics['tempo_medio_espera']:.2f}",
                'Sequencia de Execucao': sequence
        })

# Exibe os resultados

for result in results:
    print(f"\nResultados para o algoritmo: {result['Algoritmo']}")
    print(f"  Vazão: {result['Vazão']:.2f}")
    print(f"  Tempo Médio de Retorno: {result['Tempo Médio de Retorno']}")
    print(f"  Tempo Médio de Espera: {result['Tempo Médio de Espera']}")
    print("  Sequência de Execução:")
    for step in result['Sequencia de Execucao']:
        print(f"    PID: {step['pid']}, Início: {step['start']}, Fim: {step['end']}")
