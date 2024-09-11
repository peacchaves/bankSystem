from abc import ABC, abstractmethod
from datetime import datetime, date
import pytz

fuso_horario = pytz.timezone('America/Sao_Paulo')

usuarios = []
contas = []


class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor: float):
        self.valor = valor
        self.data_hora = datetime.now(fuso_horario)

    def registrar(self, conta):
        if self.valor > conta.saldo:
            raise SaldoInsuficienteError("Saldo insuficiente para realizar o saque.")
        if self.valor > conta.limite_saque:
            raise LimiteSaqueExcedidoError("O valor do saque excede o limite permitido.")
        if conta.saques_realizados >= conta.limite_saques_diarios:
            raise LimiteSaquesDiariosError("Limite de saques diários atingido.")
        if self.valor <= 0:
            raise ValorInvalidoError("O valor do saque deve ser positivo.")
        if conta.transacoes_realizadas >= 10:
            raise LimiteTransacoesDiariasError("Limite de transações diárias atingido.")

        conta.saldo -= self.valor
        conta.saques_realizados += 1
        conta.transacoes_realizadas += 1
        conta.historico.adicionar_transacao(self)
        print(f"Saque de R$ {self.valor:.2f} realizado com sucesso!")


class Deposito(Transacao):
    def __init__(self, valor: float):
        self.valor = valor
        self.data_hora = datetime.now(fuso_horario)

    def registrar(self, conta):
        if self.valor <= 0:
            raise ValorInvalidoError("O valor do depósito deve ser positivo.")
        if conta.transacoes_realizadas >= 10:
            raise LimiteTransacoesDiariasError("Limite de transações diárias atingido.")

        conta.saldo += self.valor
        conta.transacoes_realizadas += 1
        conta.historico.adicionar_transacao(self)
        print(f"Depósito de R$ {self.valor:.2f} realizado com sucesso!")


class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao: Transacao):
        self.transacoes.append(transacao)

    def listar_transacoes(self):
        if self.transacoes:
            for transacao in self.transacoes:
                print(f"{transacao.data_hora.strftime('%Y-%m-%d %H:%M:%S')} - "
                      f"{transacao.__class__.__name__}: R$ {transacao.valor:.2f}")
        else:
            print("Não foram realizadas movimentações.")


class Conta:
    def __init__(self, cliente, numero: int, agencia: str = '0001'):
        self.cliente = cliente
        self.numero = numero
        self.agencia = agencia
        self._saldo = 0.0
        self.limite_saque = 1000.0
        self.limite_saques_diarios = 3
        self.saques_realizados = 0
        self.transacoes_realizadas = 0
        self.historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor: float):
        self._saldo = valor

    def sacar(self, valor: float):
        saque = Saque(valor)
        saque.registrar(self)

    def depositar(self, valor: float):
        deposito = Deposito(valor)
        deposito.registrar(self)

    def mostrar_extrato(self):
        print(f"================ EXTRATO - Conta {self.numero} ================")
        self.historico.listar_transacoes()
        print(f"Saldo atual: R$ {self.saldo:.2f}")
        print("==============================================================")


class ContaCorrente(Conta):
    def __init__(self, cliente, numero: int, agencia: str = '0001', limite: float = 500.0, limite_saques: int = 3):
        super().__init__(cliente, numero, agencia)
        self.limite = limite
        self.limite_saques = limite_saques


class Cliente:
    def __init__(self, pessoa, endereco: str):
        self.pessoa = pessoa
        self.endereco = endereco
        self.contas = []

    @staticmethod
    def realizar_transacao(conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, data_nascimento: date, endereco: str):
        super().__init__(self, endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


class SaldoInsuficienteError(Exception):
    pass


class LimiteSaqueExcedidoError(Exception):
    pass


class LimiteSaquesDiariosError(Exception):
    pass


class LimiteTransacoesDiariasError(Exception):
    pass


class ValorInvalidoError(Exception):
    pass


def menu_principal():
    while True:
        opcao = input(
            "Escolha uma opção:\n"
            "[1] Criar Usuário\n"
            "[2] Criar Conta\n"
            "[3] Fazer Login\n"
            "[q] Sair\n"
            "=> "
        ).lower()

        if opcao == '1':
            criar_usuario()
        elif opcao == '2':
            criar_conta_corrente()
        elif opcao == '3':
            usuario = login()
            if usuario:
                conta = listar_contas_usuario(usuario)
                if conta:
                    menu_usuario(usuario, conta)
        elif opcao == 'q':
            print("Encerrando o sistema. Obrigado por usar nosso banco!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")


def criar_usuario():
    nome = input("Nome: ")
    cpf = input("CPF: ")
    data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
    endereco = input("Endereço: ")
    novo_usuario = PessoaFisica(cpf, nome, data_nascimento, endereco)
    usuarios.append(novo_usuario)
    print("Usuário criado com sucesso!")


def criar_conta_corrente():
    cpf = input("Informe o CPF do usuário para vincular à conta: ")
    usuario = next((u for u in usuarios if u.cpf == cpf), None)
    if not usuario:
        print("Usuário não encontrado.")
        return

    numero_conta = len(contas) + 1
    nova_conta = ContaCorrente(usuario, numero_conta)
    contas.append(nova_conta)
    print(f"Conta Corrente {numero_conta} criada com sucesso!")


def login():
    cpf = input("Informe seu CPF para login: ")
    usuario = next((u for u in usuarios if u.cpf == cpf), None)
    if usuario:
        print(f"Bem-vindo, {usuario.nome}!")
        return usuario
    print("Usuário não encontrado.")
    return None


def listar_contas_usuario(usuario):
    contas_usuario = [c for c in contas if c.cliente == usuario]
    if not contas_usuario:
        print("Nenhuma conta encontrada para este usuário.")
        return None

    print("Contas disponíveis:")
    for i, conta in enumerate(contas_usuario, start=1):
        print(f"[{i}] Conta {conta.numero}")

    escolha = int(input("Selecione uma conta: ")) - 1
    if 0 <= escolha < len(contas_usuario):
        return contas_usuario[escolha]
    print("Opção inválida.")
    return None


def menu_usuario(usuario, conta):
    while True:
        opcao = input(
            f"\nOlá, {usuario.nome}! Você está acessando a Conta: {conta.numero}\n"
            "[d] Depositar\n[s] Sacar\n[e] Extrato\n[q] Sair\n=> "
        ).lower()

        if opcao == 'd':
            valor = float(input("Informe o valor do depósito: "))
            transacao = Deposito(valor)
            Cliente.realizar_transacao(conta, transacao)

        elif opcao == 's':
            valor = float(input("Informe o valor do saque: "))
            transacao = Saque(valor)
            Cliente.realizar_transacao(conta, transacao)

        elif opcao == 'e':
            conta.mostrar_extrato()

        elif opcao == 'q':
            print("Encerrando o acesso. Obrigado!")
            break

        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")


menu_principal()
