# app/utils/algoritmos.py

# -------------------------
# LISTA ENCADEADA SIMPLES
# -------------------------

class No:
    def __init__(self, tarefa):
        self.tarefa = tarefa
        self.proximo = None

class ListaEncadeadaSimples:
    def __init__(self):
        self.inicio = None

    def inserir(self, tarefa):
        novo = No(tarefa)
        if self.inicio is None:
            self.inicio = novo
        else:
            atual = self.inicio
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo

    def listar(self):
        atual = self.inicio
        resultado = []
        while atual:
            resultado.append(atual.tarefa)
            atual = atual.proximo
        return resultado

# -------------------------
# BUSCA LINEAR
# -------------------------

def busca_linear(lista_de_tarefas, chave_nome):
    for tarefa in lista_de_tarefas:
        if tarefa.name.lower() == chave_nome.lower():
            return tarefa
    return None

# -------------------------
# BUBBLE SORT
# -------------------------

def bubble_sort(lista, chave=lambda x: x.name):
    n = len(lista)
    for i in range(n):
        for j in range(0, n-i-1):
            if chave(lista[j]) > chave(lista[j+1]):
                lista[j], lista[j+1] = lista[j+1], lista[j]
    return lista
