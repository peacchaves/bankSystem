import pytest
from datetime import datetime, timedelta
from main import PessoaFisica, Conta, SaldoInsuficienteError, LimiteSaqueExcedidoError, LimiteSaquesDiariosError, ValorInvalidoError, LimiteTransacoesDiariasError, Deposito, Saque, formatar_moeda, Historico, fuso_horario

@pytest.fixture
def usuario_exemplo():
    return PessoaFisica(cpf='12345678901', nome='João da Silva', data_nascimento='01/01/1990', endereco='Rua Exemplo, 123')

@pytest.fixture
def conta_exemplo(usuario_exemplo):
    return Conta(cliente=usuario_exemplo, numero=1)

def test_criar_usuario(usuario_exemplo):
    assert usuario_exemplo.nome == 'João da Silva'
    assert usuario_exemplo.cpf == '12345678901'
    assert usuario_exemplo.data_nascimento == datetime.strptime('01/01/1990', '%d/%m/%Y').date()

def test_criar_conta(conta_exemplo):
    assert conta_exemplo.cliente.nome == 'João da Silva'
    assert conta_exemplo.numero == 1
    assert conta_exemplo.saldo == 0.0

def test_deposito(conta_exemplo):
    deposito = Deposito(100.0)
    deposito.registrar(conta_exemplo)
    assert conta_exemplo.saldo == 100.0
    assert len(conta_exemplo.historico.transacoes) == 1

def test_saque_valido(conta_exemplo):
    conta_exemplo.saldo = 100.0
    saque = Saque(50.0)
    saque.registrar(conta_exemplo)
    assert conta_exemplo.saldo == 50.0
    assert len(conta_exemplo.historico.transacoes) == 1

def test_saque_saldo_insuficiente(conta_exemplo):
    conta_exemplo.saldo = 30.0
    with pytest.raises(SaldoInsuficienteError):
        saque = Saque(50.0)
        saque.registrar(conta_exemplo)

def test_saque_limite_diario(conta_exemplo):
    conta_exemplo.saldo = 1000.0
    for _ in range(3):
        saque = Saque(100.0)
        saque.registrar(conta_exemplo)

    with pytest.raises(LimiteSaquesDiariosError):
        saque = Saque(100.0)
        saque.registrar(conta_exemplo)

def test_deposito_valor_invalido(conta_exemplo):
    with pytest.raises(ValorInvalidoError):
        deposito = Deposito(-100.0)
        deposito.registrar(conta_exemplo)

def test_limite_transacoes_diarias(conta_exemplo):
    conta_exemplo.saldo = 1000.0
    for _ in range(10):
        deposito = Deposito(10.0)
        deposito.registrar(conta_exemplo)

    with pytest.raises(LimiteTransacoesDiariasError):
        deposito = Deposito(10.0)
        deposito.registrar(conta_exemplo)

def test_formatar_moeda():
    assert formatar_moeda(1234.567) == "R$ 1234.57"
