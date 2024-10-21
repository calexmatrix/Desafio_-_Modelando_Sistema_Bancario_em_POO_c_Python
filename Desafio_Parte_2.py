import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self.saldo:
            print("\n@@@ Saldo insuficiente. @@@")
            return False
        if valor <= 0:
            print("\n@@@ Valor inválido. @@@")
            return False
        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Valor inválido. @@@")
            return False
        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )
        if valor > self._limite:
            print("\n@@@ Valor do saque excede o limite. @@@")
            return False
        if numero_saques >= self._limite_saques:
            print("\n@@@ Limite de saques excedido. @@@")
            return False
        return super().sacar(valor)

    def __str__(self):
        return f"Agência: {self.agencia}\nC/C: {self.numero}\nTitular: {self.cliente.nome}"

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

def menu():
    return input(textwrap.dedent("""
    \n=============== MENU ================
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Novo usuário
    [5] Nova conta
    [6] Listar contas
    [7] Sair
    ======================================
    => """))

def filtrar_cliente(cpf, clientes):
    return next((cliente for cliente in clientes if cliente.cpf == cpf), None)

def selecionar_conta(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta. @@@")
        return None
    if len(cliente.contas) == 1:
        return cliente.contas[0]
    print("\nEscolha a conta:")
    for i, conta in enumerate(cliente.contas, 1):
        print(f"[{i}] Conta {conta.numero}")
    opcao = int(input("=> "))
    return cliente.contas[opcao - 1]

def transacao_valida(clientes, mensagem_valor, tipo_transacao):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return
    conta = selecionar_conta(cliente)
    if not conta:
        return
    valor = float(input(mensagem_valor))
    transacao = tipo_transacao(valor)
    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return
    conta = selecionar_conta(cliente)
    if not conta:
        return
    print("\n======= EXTRATO =======")
    transacoes = conta.historico.transacoes
    if not transacoes:
        print("Nenhuma transação realizada.")
    else:
        for transacao in transacoes:
            print(f"{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f} em {transacao['data']}")
    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("========================")

def criar_cliente(clientes):
    cpf = input("Informe o CPF: ")
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Cliente com esse CPF já existe. @@@")
        return
    nome = input("Informe o nome: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço: ")
    clientes.append(PessoaFisica(nome, data_nascimento, cpf, endereco))
    print("\n=== Cliente criado com sucesso! ===")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n@@@ Cliente não encontrado. @@@")
        return
    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    if not contas:
        print("\n@@@ Nenhuma conta cadastrada. @@@")
    for conta in contas:
        print("=" * 30)
        print(conta)

def main():
    clientes, contas = [], []
    while True:
        opcao = menu()
        if opcao == "1":
            transacao_valida(clientes, "Informe o valor do depósito: ", Deposito)
        elif opcao == "2":
            transacao_valida(clientes, "Informe o valor do saque: ", Saque)
        elif opcao == "3":
            exibir_extrato(clientes)
        elif opcao == "4":
            criar_cliente(clientes)
        elif opcao == "5":
            criar_conta(len(contas) + 1, clientes, contas)
        elif opcao == "6":
            listar_contas(contas)
        elif opcao == "7":
            break
        else:
            print("\n@@@ Operação inválida! @@@")

main()
