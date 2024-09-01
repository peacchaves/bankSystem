import unittest
from unittest.mock import patch
from datetime import datetime
from functions import (
    criar_usuario, criar_conta_corrente, depositar, sacar,
    SaldoInsuficienteError, verificar_limite_transacoes
)


class TestBankSystem(unittest.TestCase):

    def setUp(self):
        # Configuração inicial para cada teste
        self.usuarios = []
        self.contas = []
        self.saldo_atual = 1000.0
        self.extrato_movimentacoes = []
        self.transacoes_realizadas = 0
        self.saques_realizados = 0
        self.fuso_horario = datetime.now().astimezone().tzinfo

    @patch('builtins.input', side_effect=['João Silva', '12345678901', '01/01/1990',
                                          'Rua A, 123, Bairro B', '12345678', 'Cidade C', 'SP'])
    def test_criar_usuario(self, _):
        criar_usuario(self.usuarios)
        self.assertEqual(len(self.usuarios), 1)
        self.assertEqual(self.usuarios[0]['nome'], 'João Silva')
        self.assertEqual(self.usuarios[0]['cpf'], '12345678901')
        self.assertEqual(self.usuarios[0]['data_nascimento'], '01/01/1990')
        self.assertEqual(self.usuarios[0]['endereco']['logradouro'], 'Rua A, 123, Bairro B')
        self.assertEqual(self.usuarios[0]['endereco']['cep'], '12345678')
        self.assertEqual(self.usuarios[0]['endereco']['cidade'], 'Cidade C')
        self.assertEqual(self.usuarios[0]['endereco']['estado'], 'SP')

    @patch('builtins.input', side_effect=['12345678901'])
    def test_criar_conta_corrente(self, _):
        criar_usuario(self.usuarios)
        criar_conta_corrente(self.contas, self.usuarios)
        self.assertEqual(len(self.contas), 1)
        self.assertEqual(self.contas[0]['usuario']['cpf'], '12345678901')
        self.assertEqual(self.contas[0]['numero'], 1)

    def test_depositar(self):
        valor_deposito = 500.0
        self.saldo_atual, self.extrato_movimentacoes, self.transacoes_realizadas, _ = depositar(
            self.saldo_atual, self.extrato_movimentacoes, valor_deposito, self.transacoes_realizadas, self.fuso_horario)
        self.assertEqual(self.saldo_atual, 1500.0)
        self.assertEqual(len(self.extrato_movimentacoes), 1)
        self.assertIn("Depósito: R$ 500.00", self.extrato_movimentacoes[0])

    def test_sacar(self):
        valor_saque = 200.0
        self.saldo_atual, self.extrato_movimentacoes, self.saques_realizados, self.transacoes_realizadas, _ = sacar(
            saldo_atual=self.saldo_atual, extrato_movimentacoes=self.extrato_movimentacoes, valor_saque=valor_saque,
            limite_saque=500.0, saques_realizados=self.saques_realizados,
            limite_saques_diarios=3, transacoes_realizadas=self.transacoes_realizadas,
            fuso_horario=self.fuso_horario)
        self.assertEqual(self.saldo_atual, 800.0)
        self.assertEqual(len(self.extrato_movimentacoes), 1)
        self.assertEqual(self.saques_realizados, 1)

    def test_sacar_saldo_insuficiente(self):
        with self.assertRaises(SaldoInsuficienteError):
            sacar(saldo_atual=self.saldo_atual, extrato_movimentacoes=self.extrato_movimentacoes, valor_saque=1500.0,
                  limite_saque=500.0, saques_realizados=self.saques_realizados,
                  limite_saques_diarios=3, transacoes_realizadas=self.transacoes_realizadas,
                  fuso_horario=self.fuso_horario)

    def test_verificar_limite_transacoes(self):
        hora_ultima_transacao = datetime.now(self.fuso_horario)
        horas_restantes, minutos_restantes = verificar_limite_transacoes(hora_ultima_transacao, self.fuso_horario)
        self.assertEqual(horas_restantes, 0)
        self.assertEqual(minutos_restantes, 0)


if __name__ == '__main__':
    unittest.main()
