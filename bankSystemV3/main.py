import re
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
import pytz
from enum import Enum
from typing import List

fuso_horario = pytz.timezone('America/Sao_Paulo')

usuarios: List['PessoaFisica'] = []
contas: List['Conta'] = []

class SaldoInsuficienteError(Exception):
    pass

class LimiteSaqueExcedidoError(Exception):
    pass

class LimiteSaquesDiariosError(Exception):
    pass

class ValorInvalidoError(Exception):
    pass

class LimiteTransacoesDiariasError(Exception):
    pass

LIMITE_TRANSACOES_DIARIAS = 10
LIMITE_SAQUES_DIARIOS = 3
LIMITE_VALOR_SAQUE = 500.0

class OpcaoMenu(Enum):
    CRIAR_USUARIO = '1'
    CRIAR_CONTA = '2'
    LOGIN = '3'
    SAIR = 'q'

class OpcaoMenuUsuario(Enum):
    DEPOSITAR = 'd'
    SACAR = 's'
    EXTRATO = 'e'
    SAIR = 'q'

class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor: float):
        self.valor = valor
        self.data_hora = datetime.now(fuso_horario)

    def registrar(self, conta):
        self._validar_saque(conta)
        conta.saldo -= self.valor
        conta.saques_realizados += 1
        conta.transacoes_realizadas += 1
        conta.historico.adicionar_transacao(self)
        print(f"Saque de {formatar_moeda(self.valor)} realizado com sucesso!")

    def _validar_saque(self, conta):
        if self.valor > conta.saldo:
            raise SaldoInsuficienteError("Saldo insuficiente para realizar o saque.")
        if self.valor > LIMITE_VALOR_SAQUE:
            raise LimiteSaqueExcedidoError(f"O valor do saque excede o limite permitido de {formatar_moeda(LIMITE_VALOR_SAQUE)}.")
        if conta.saques_realizados >= LIMITE_SAQUES_DIARIOS:
            tempo_restante = self._calcular_tempo_restante()
            raise LimiteSaquesDiariosError(f"Limite de saques diários atingido. Tente novamente em {tempo_restante}.")
        if self.valor <= 0:
            raise ValorInvalidoError("O valor do saque deve ser positivo.")
        if conta.transacoes_realizadas >= LIMITE_TRANSACOES_DIARIAS:
            raise LimiteTransacoesDiariasError("Limite de transações diárias atingido.")

    def _calcular_tempo_restante(self):
        agora = datetime.now(fuso_horario)
        meia_noite = (agora + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tempo_restante = meia_noite - agora
        horas, resto = divmod(tempo_restante.seconds, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

class Deposito(Transacao):
    def __init__(self, valor: float):
        self.valor = valor
        self.data_hora = datetime.now(fuso_horario)

    def registrar(self, conta):
        self._validar_deposito(conta)
        conta.saldo += self.valor
        conta.transacoes_realizadas += 1
        conta.historico.adicionar_transacao(self)
        print(f"Depósito de {formatar_moeda(self.valor)} realizado com sucesso!")

    def _validar_deposito(self, conta):
        if self.valor <= 0:
            raise ValorInvalidoError("O valor do depósito deve ser positivo.")
        if conta.transacoes_realizadas >= LIMITE_TRANSACOES_DIARIAS:
            raise LimiteTransacoesDiariasError("Limite de transações diárias atingido.")

class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao: Transacao):
        self.transacoes.append(transacao)

    def listar_transacoes(self):
        if self.transacoes:
            for transacao in self.transacoes:
                print(f"{transacao.data_hora.strftime('%Y-%m-%d %H:%M:%S')} - "
                      f"{transacao.__class__.__name__}: {formatar_moeda(transacao.valor)}")
        else:
            print("Não foram realizadas movimentações.")

class Conta:
    def __init__(self, cliente, numero: int, agencia: str = '0001'):
        self.cliente = cliente
        self.numero = numero
        self.agencia = agencia
        self._saldo = 0.0
        self.limite_saque = LIMITE_VALOR_SAQUE
        self.limite_saques_diarios = LIMITE_SAQUES_DIARIOS
        self.saques_realizados = 0
        self.transacoes_realizadas = 0
        self.historico = Historico()
        self.ultima_data_saque = None
        self.ultima_data_transacao = None

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor: float):
        self._saldo = valor

    def sacar(self, valor: float):
        agora = datetime.now(fuso_horario)
        if self.ultima_data_saque is None or agora.date() > self.ultima_data_saque.date():
            self.saques_realizados = 0
        self.ultima_data_saque = agora
        
        if self.ultima_data_transacao is None or agora.date() > self.ultima_data_transacao.date():
            self.transacoes_realizadas = 0
        self.ultima_data_transacao = agora
        
        saque = Saque(valor)
        saque.registrar(self)

    def depositar(self, valor: float):
        agora = datetime.now(fuso_horario)
        if self.ultima_data_transacao is None or agora.date() > self.ultima_data_transacao.date():
            self.transacoes_realizadas = 0
        self.ultima_data_transacao = agora
        
        deposito = Deposito(valor)
        deposito.registrar(self)

    def mostrar_extrato(self):
        print(f"================ EXTRATO - Conta {self.numero} ================")
        self.historico.listar_transacoes()
        print(f"Saldo atual: {formatar_moeda(self.saldo)}")
        print("==============================================================")

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
    def __init__(self, cpf: str, nome: str, data_nascimento: str, endereco: str):
        super().__init__(self, endereco)
        self.cpf = self._validar_cpf(cpf)
        self.nome = nome
        self.data_nascimento = self._validar_data_nascimento(data_nascimento)

    @staticmethod
    def _validar_cpf(cpf: str) -> str:
        cpf_limpo = re.sub(r'\D', '', cpf)
        if len(cpf_limpo) != 11:
            raise ValueError("CPF inválido. Deve conter 11 dígitos.")
        return cpf_limpo

    @staticmethod
    def _validar_data_nascimento(data_nascimento: str) -> date:
        try:
            return datetime.strptime(data_nascimento, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError("Data de nascimento inválida. Use o formato dd/mm/aaaa.")

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:.2f}"

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

        if opcao == OpcaoMenu.CRIAR_USUARIO.value:
            criar_usuario()
        elif opcao == OpcaoMenu.CRIAR_CONTA.value:
            criar_conta_corrente()
        elif opcao == OpcaoMenu.LOGIN.value:
            usuario = login()
            if usuario:
                conta = listar_contas_usuario(usuario)
                if conta:
                    menu_usuario(usuario, conta)
        elif opcao == OpcaoMenu.SAIR.value:
            print("Encerrando o sistema. Obrigado por usar nosso banco!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")

def criar_usuario():
    try:
        nome = input("Nome: ")
        cpf = input("CPF: ")
        data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
        endereco = input("Endereço: ")
        novo_usuario = PessoaFisica(cpf, nome, data_nascimento, endereco)
        usuarios.append(novo_usuario)
        print("Usuário criado com sucesso!")
    except ValueError as e:
        print(f"Erro ao criar usuário: {str(e)}")

def criar_conta_corrente():
    try:
        cpf = input("Informe o CPF do usuário para vincular à conta: ")
        usuario = next((u for u in usuarios if u.cpf == cpf), None)
        if not usuario:
            print("Usuário não encontrado.")
            return

        numero_conta = len(contas) + 1
        nova_conta = Conta(usuario, numero_conta)
        contas.append(nova_conta)
        print(f"Conta Corrente {numero_conta} criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar conta: {str(e)}")

def login():
    try:
        cpf = input("Informe seu CPF para login: ")
        usuario = next((u for u in usuarios if u.cpf == cpf), None)
        if usuario:
            print(f"Bem-vindo, {usuario.nome}!")
            return usuario
        print("Usuário não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao fazer login: {str(e)}")
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
            f"Saques disponíveis hoje: {LIMITE_SAQUES_DIARIOS - conta.saques_realizados}\n"
            "[d] Depositar\n[s] Sacar\n[e] Extrato\n[q] Sair\n=> "
        ).lower()

        if opcao == OpcaoMenuUsuario.DEPOSITAR.value:
            valor = float(input("Informe o valor do depósito: "))
            transacao = Deposito(valor)
            Cliente.realizar_transacao(conta, transacao)

        elif opcao == OpcaoMenuUsuario.SACAR.value:
            valor = float(input("Informe o valor do saque: "))
            try:
                transacao = Saque(valor)
                Cliente.realizar_transacao(conta, transacao)
            except (SaldoInsuficienteError, LimiteSaqueExcedidoError, 
                    LimiteSaquesDiariosError, ValorInvalidoError, 
                    LimiteTransacoesDiariasError) as e:
                print(f"Erro ao realizar saque: {str(e)}")

        elif opcao == OpcaoMenuUsuario.EXTRATO.value:
            conta.mostrar_extrato()

        elif opcao == OpcaoMenuUsuario.SAIR.value:
            print("Encerrando o acesso. Obrigado!")
            break

        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")

menu_principal()
