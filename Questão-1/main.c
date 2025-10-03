#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define NUM_PROCESSOS 5
#define CUSTO_SWITCH 1
#define TEMPO_NAO_INICIADO -1
#define THROUGHPUT_WINDOW_T 100

typedef struct {
    char pid[5];               
    int tempo_chegada;
    int tempo_burst;
    int tempo_restante;
    int tempo_concluido;
    int tempo_retorno;
    int tempo_espera;
    int tempo_inicio;
} Processo;

typedef struct {
    char pid[5];
    int inicio;
    int fim;
} GanttEntry;

GanttEntry gantt_log[200];
int gantt_count = 0;
int tempo_final_simulacao = 0;

void log_gantt(const char *pid, int inicio, int fim) {
    if (gantt_count < 200) {
        strncpy(gantt_log[gantt_count].pid, pid, 4);
        gantt_log[gantt_count].pid[4] = '\0';
        gantt_log[gantt_count].inicio = inicio;
        gantt_log[gantt_count].fim = fim;
        gantt_count++;
    }
}

void carregar_processos(Processo p[]) {
    strcpy(p[0].pid, "P01"); p[0].tempo_chegada = 0; p[0].tempo_burst = 5;
    strcpy(p[1].pid, "P02"); p[1].tempo_chegada = 1; p[1].tempo_burst = 17;
    strcpy(p[2].pid, "P03"); p[2].tempo_chegada = 2; p[2].tempo_burst = 3;
    strcpy(p[3].pid, "P04"); p[3].tempo_chegada = 4; p[3].tempo_burst = 22;
    strcpy(p[4].pid, "P05"); p[4].tempo_chegada = 6; p[4].tempo_burst = 7;

    for (int i = 0; i < NUM_PROCESSOS; i++) {
        p[i].tempo_restante = p[i].tempo_burst;
        p[i].tempo_concluido = TEMPO_NAO_INICIADO;
        p[i].tempo_retorno = TEMPO_NAO_INICIADO;
        p[i].tempo_espera = TEMPO_NAO_INICIADO;
        p[i].tempo_inicio = TEMPO_NAO_INICIADO;
    }

    gantt_count = 0;
    tempo_final_simulacao = 0;
}

float calcular_std(float media, const int tempos[], int n) {
    if (n == 0) return 0.0f;
    float soma = 0.0f;
    for (int i = 0; i < n; i++) soma += powf(tempos[i] - media, 2.0f);
    return sqrtf(soma / (n > 1 ? (n - 1) : 1));
}

void exibir_gantt() {
    if (gantt_count == 0) {
        printf("\n--- Diagrama de Gantt (vazio) ---\n");
        return;
    }

    const int CELL_W = 8; 
    printf("\nDIAGRAMA DE GANTT:\n");

    for (int i = 0; i < gantt_count; i++) {
        printf("| %-*s ", CELL_W - 2, gantt_log[i].pid); 
    }
    printf("|\n");

    printf("%d", gantt_log[0].inicio);
    for (int i = 0; i < gantt_count; i++) {
        printf("%*d", CELL_W, gantt_log[i].fim);
    }
    printf("\n");
}

void calcular_e_exibir_metricas(Processo p[], const char *algoritmo) {
    float total_tr = 0.0f, total_te = 0.0f;
    int tempos_tr[NUM_PROCESSOS];
    int tempos_te[NUM_PROCESSOS];

    for (int i = 0; i < NUM_PROCESSOS; i++) {
        if (p[i].tempo_concluido != TEMPO_NAO_INICIADO)
            p[i].tempo_retorno = p[i].tempo_concluido - p[i].tempo_chegada;
        else
            p[i].tempo_retorno = TEMPO_NAO_INICIADO;

        if (p[i].tempo_retorno != TEMPO_NAO_INICIADO)
            p[i].tempo_espera = p[i].tempo_retorno - p[i].tempo_burst;
        else
            p[i].tempo_espera = TEMPO_NAO_INICIADO;
    }

    const int PID_W = 4;
    const int CHEG_W = 8;
    const int BURST_W = 7;
    const int CONCL_W = 10;
    const int RET_W = 8;
    const int ESP_W = 7;

    int table_width = PID_W + CHEG_W + BURST_W + CONCL_W + RET_W + ESP_W + 7 * 3; 

    for (int i = 0; i < 60; i++) putchar('=');
    printf("\n");
    printf("     RESULTADOS DO ESCALONAMENTO: %s\n", algoritmo);
    for (int i = 0; i < 60; i++) putchar('=');
    printf("\n");

    printf("| %-4s | %6s | %5s | %8s | %6s | %5s |\n",
           "PID", "Chegada", "Burst", "Conclusao", "Retorno", "Espera");
    printf("|------|--------|-------|----------|--------|-------|\n");

    for (int i = 0; i < NUM_PROCESSOS; i++) {
        const char *conclu = (p[i].tempo_concluido == TEMPO_NAO_INICIADO) ? "-" : "";
        const char *retorno = (p[i].tempo_retorno == TEMPO_NAO_INICIADO) ? "-" : "";
        const char *espera = (p[i].tempo_espera == TEMPO_NAO_INICIADO) ? "-" : "";

        int tr = (p[i].tempo_retorno == TEMPO_NAO_INICIADO) ? 0 : p[i].tempo_retorno;
        int te = (p[i].tempo_espera == TEMPO_NAO_INICIADO) ? 0 : p[i].tempo_espera;

        total_tr += tr;
        total_te += te;
        tempos_tr[i] = tr;
        tempos_te[i] = te;

        if (p[i].tempo_concluido == TEMPO_NAO_INICIADO) {
            printf("| %-4s | %6d | %5d | %8s | %6s | %5s |\n",
                   p[i].pid,
                   p[i].tempo_chegada,
                   p[i].tempo_burst,
                   "-",
                   "-",
                   "-");
        } else {
            printf("| %-4s | %6d | %5d | %8d | %6d | %5d |\n",
                   p[i].pid,
                   p[i].tempo_chegada,
                   p[i].tempo_burst,
                   p[i].tempo_concluido,
                   p[i].tempo_retorno,
                   p[i].tempo_espera);
        }
    }

    float media_te = total_te / NUM_PROCESSOS;
    float media_tr = total_tr / NUM_PROCESSOS;
    float std_te = calcular_std(media_te, tempos_te, NUM_PROCESSOS);
    float std_tr = calcular_std(media_tr, tempos_tr, NUM_PROCESSOS);

    int concluidos_na_janela = 0;
    for (int i = 0; i < NUM_PROCESSOS; i++) {
        if (p[i].tempo_concluido != TEMPO_NAO_INICIADO && p[i].tempo_concluido <= THROUGHPUT_WINDOW_T) {
            concluidos_na_janela++;
        }
    }

    float tempo_base_vazao = (tempo_final_simulacao > 0 && tempo_final_simulacao < THROUGHPUT_WINDOW_T)
                             ? (float)tempo_final_simulacao : (float)THROUGHPUT_WINDOW_T;
    float vazao = (tempo_base_vazao > 0.0f) ? ((float)concluidos_na_janela / tempo_base_vazao) : 0.0f;

    printf("-------------------------------------------------------\n");
    printf("  Tempo Médio de Espera (TE): %.2f (+/- %.2f std)\n", media_te, std_te);
    printf("  Tempo Médio de Retorno (TR): %.2f (+/- %.2f std)\n", media_tr, std_tr);
    printf("  Vazão (Throughput): %.4f processos/unidade de tempo (Janela T=%d)\n", vazao, (int)tempo_base_vazao);
    for (int i = 0; i < 60; i++) putchar('=');
    printf("\n");

    exibir_gantt();
}


void simular_fcfs(Processo p[]) {
    int tempo_atual = 0;

    printf("\n--- Simulação FCFS ---\n");

    for (int i = 0; i < NUM_PROCESSOS; i++) {

        if (tempo_atual < p[i].tempo_chegada)
            tempo_atual = p[i].tempo_chegada;

        int inicio_execucao = tempo_atual;

        if (p[i].tempo_inicio == TEMPO_NAO_INICIADO)
            p[i].tempo_inicio = inicio_execucao;

        tempo_atual += p[i].tempo_burst;
        p[i].tempo_restante = 0;
        p[i].tempo_concluido = tempo_atual;

        log_gantt(p[i].pid, inicio_execucao, tempo_atual);

        if (i < NUM_PROCESSOS - 1)
            tempo_atual += CUSTO_SWITCH;
    }
    tempo_final_simulacao = tempo_atual;
}

void simular_sjf(Processo p[]) {
    int tempo_atual = 0;
    int concluidos = 0;
    int proc_anterior = TEMPO_NAO_INICIADO;

    printf("\n--- Simulação SJF (Não Preemptivo) ---\n");

    while (concluidos < NUM_PROCESSOS) {
        int menor_burst = 99999;
        int proc_escolhido = TEMPO_NAO_INICIADO;

        for (int i = 0; i < NUM_PROCESSOS; i++) {
            if (p[i].tempo_restante > 0 && p[i].tempo_chegada <= tempo_atual) {
                if (p[i].tempo_burst < menor_burst) {
                    menor_burst = p[i].tempo_burst;
                    proc_escolhido = i;
                }
            }
        }

        if (proc_escolhido == TEMPO_NAO_INICIADO) {
            tempo_atual++;
            continue;
        }

        if (concluidos > 0) {
            if (proc_anterior != proc_escolhido) {
                tempo_atual += CUSTO_SWITCH;
            }
        }

        int inicio_execucao = tempo_atual;

        if (p[proc_escolhido].tempo_inicio == TEMPO_NAO_INICIADO)
            p[proc_escolhido].tempo_inicio = inicio_execucao;

        tempo_atual += p[proc_escolhido].tempo_burst;
        p[proc_escolhido].tempo_restante = 0;
        p[proc_escolhido].tempo_concluido = tempo_atual;
        concluidos++;

        log_gantt(p[proc_escolhido].pid, inicio_execucao, tempo_atual);
        proc_anterior = proc_escolhido;
    }
    tempo_final_simulacao = tempo_atual;
}

void simular_rr(Processo p[], int quantum) {
    int tempo_atual = 0;
    int concluidos = 0;
    int fila[NUM_PROCESSOS * 10];
    int head = 0, tail = 0;
    int entrou_na_fila[NUM_PROCESSOS] = {0};
    int proc_anterior = TEMPO_NAO_INICIADO;

    printf("\n--- Simulação Round Robin (Quantum = %d) ---\n", quantum);

    for (int i = 0; i < NUM_PROCESSOS; i++) {
        if (p[i].tempo_chegada == 0) {
            fila[tail++] = i;
            entrou_na_fila[i] = 1;
        }
    }

    while (concluidos < NUM_PROCESSOS) {
        if (head == tail) {
            int proximo_chegada = 99999;
            for (int i = 0; i < NUM_PROCESSOS; i++) {
                if (!entrou_na_fila[i] && p[i].tempo_chegada < proximo_chegada) {
                    proximo_chegada = p[i].tempo_chegada;
                }
            }
            if (proximo_chegada == 99999) break;
            tempo_atual = proximo_chegada;

            for (int i = 0; i < NUM_PROCESSOS; i++) {
                if (!entrou_na_fila[i] && p[i].tempo_chegada <= tempo_atual) {
                    fila[tail++] = i;
                    entrou_na_fila[i] = 1;
                }
            }
            continue;
        }

        int proc = fila[head++];

        if (proc_anterior != TEMPO_NAO_INICIADO && proc_anterior != proc) {
             tempo_atual += CUSTO_SWITCH;
        }

        int inicio_execucao = tempo_atual;

        if (p[proc].tempo_inicio == TEMPO_NAO_INICIADO)
            p[proc].tempo_inicio = inicio_execucao;

        int exec = (p[proc].tempo_restante < quantum) ? p[proc].tempo_restante : quantum;

        tempo_atual += exec;
        p[proc].tempo_restante -= exec;

        for (int i = 0; i < NUM_PROCESSOS; i++) {
            if (!entrou_na_fila[i] && p[i].tempo_chegada > inicio_execucao && p[i].tempo_chegada <= tempo_atual) {
                fila[tail++] = i;
                entrou_na_fila[i] = 1;
            }
        }

        if (p[proc].tempo_restante == 0) {
            p[proc].tempo_concluido = tempo_atual;
            concluidos++;
        } else {
            fila[tail++] = proc;
        }

        log_gantt(p[proc].pid, inicio_execucao, tempo_atual);
        proc_anterior = proc;
    }
    tempo_final_simulacao = tempo_atual;
}

int main() {
    Processo processos[NUM_PROCESSOS];
    int rr_quantums[] = {1, 2, 4, 8, 16};

    carregar_processos(processos);
    simular_fcfs(processos);
    calcular_e_exibir_metricas(processos, "FCFS (First Come, First Served)");

    carregar_processos(processos);
    simular_sjf(processos);
    calcular_e_exibir_metricas(processos, "SJF (Shortest Job First - Não Preemptivo)");

    for (int i = 0; i < (int)(sizeof(rr_quantums) / sizeof(rr_quantums[0])); i++) {
        carregar_processos(processos);
        simular_rr(processos, rr_quantums[i]);
        char nome[80];
        sprintf(nome, "Round Robin (Quantum = %d)", rr_quantums[i]);
        calcular_e_exibir_metricas(processos, nome);
    }

    return 0;
}
