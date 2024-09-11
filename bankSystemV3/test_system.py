import unittest
from unittest.mock import patch
from functions import (
    Cliente, PessoaFisica, ContaCorrente, Deposito, Saque,
    SaldoInsuficienteError, LimiteSaqueExcedidoError, LimiteSaquesDiariosError,
    ValorInvalidoError, LimiteTransacoesDiariasError
)


class TestBankSystem(unittest.TestCase):

    def setUp(self):
        self.usuario = Cliente(PessoaFisica("12345678901", "João Silva", "01/01/1990"), "Rua A, 123, Bairro B")
        self.conta = ContaCorrente(self.usuario)
        self.usuarios = [self.usuario]
        self.contas = [self.conta]

    def test_criar_usuario(self):
        self.assertEqual(self.usuario.pessoa.nome, 'João Silva')
        self.assertEqual(self.usuario.pessoa.cpf, '12345678901')
        self.assertEqual(self.usuario.pessoa.data_nascimento, '01/01/1990')
        self.assertEqual(self.usuario.endereco, 'Rua A, 123, Bairro B')

    def test_criar_conta_corrente(self):
        self.assertEqual(self.conta.usuario, self.usuario)
        self.assertEqual(self.conta.numero, 1)

    def test_depositar(self):
        deposito = Deposito(500.0)
        self.usuario.realizar_transacao(self.conta, deposito)
        self.assertEqual(self.conta.saldo, 500.0)

    def test_sacar(self):
        deposito = Deposito(1000.0)
        self.usuario.realizar_transacao(self.conta, deposito)
        saque = Saque(200.0)
        self.usuario.realizar_transacao(self.conta, saque)
        self.assertEqual(self.conta.saldo, 800.0)

    def test_sacar_saldo_insuficiente(self):
        saque = Saque(1500.0)
        with self.assertRaises(SaldoInsuficienteError):
            self.usuario.realizar_transacao(self.conta, saque)


if __name__ == '__main__':
    unittest.main()
