from datetime import datetime, timedelta


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


def depositar(saldo_atual, extrato_movimentacoes, valor_deposito, transacoes_realizadas, fuso_horario):
    if valor_deposito <= 0:
        raise ValorInvalidoError("O valor do depósito deve ser positivo.")
    if transacoes_realizadas >= 10:
        raise LimiteTransacoesDiariasError("Limite de transações diárias atingido.")

    saldo_atual += valor_deposito
    hora_atual = datetime.now(fuso_horario)
    extrato_movimentacoes.append(f"{hora_atual.strftime('%Y-%m-%d %H:%M:%S')} - Depósito: R$ {valor_deposito:.2f}")
    print(f"Depósito de R$ {valor_deposito:.2f} realizado com sucesso!")
    transacoes_realizadas += 1
    return saldo_atual, extrato_movimentacoes, transacoes_realizadas, hora_atual


def sacar(saldo_atual, extrato_movimentacoes, valor_saque, limite_saque, saques_realizados, limite_saques_diarios,
          transacoes_realizadas, fuso_horario):
    if valor_saque > saldo_atual:
        raise SaldoInsuficienteError("Saldo insuficiente para realizar o saque.")
    if valor_saque > limite_saque:
        raise LimiteSaqueExcedidoError("O valor do saque excede o limite permitido.")
    if saques_realizados >= limite_saques_diarios:
        raise LimiteSaquesDiariosError("Limite de saques diários atingido.")
    if valor_saque <= 0:
        raise ValorInvalidoError("O valor do saque deve ser positivo.")
    if transacoes_realizadas >= 10:
        raise LimiteTransacoesDiariasError("Limite de transações diárias atingido.")

    saldo_atual -= valor_saque
    hora_atual = datetime.now(fuso_horario)
    extrato_movimentacoes.append(f"{hora_atual.strftime('%Y-%m-%d %H:%M:%S')} - Saque: R$ {valor_saque:.2f}")
    saques_realizados += 1
    transacoes_realizadas += 1
    print(f"Saque de R$ {valor_saque:.2f} realizado com sucesso!")
    return saldo_atual, extrato_movimentacoes, saques_realizados, transacoes_realizadas, hora_atual


def mostrar_extrato(extrato_movimentacoes, saldo_atual):
    print("\n================ EXTRATO ================")
    if extrato_movimentacoes:
        for movimentacao in extrato_movimentacoes:
            print(movimentacao)
    else:
        print("Não foram realizadas movimentações.")
    print(f"\nSaldo atual: R$ {saldo_atual:.2f}")
    print("==========================================")


def identificar_usuario():
    nome = input("Por favor, informe seu nome: ")
    if not nome.strip():
        raise ValorInvalidoError("O nome do usuário não pode estar vazio.")
    print(f"Bem-vindo(a), {nome}!")
    return nome


def verificar_limite_transacoes(hora_ultima_transacao, fuso_horario):
    agora = datetime.now(fuso_horario)
    proxima_meia_noite = (hora_ultima_transacao + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    horas_restantes = (proxima_meia_noite - agora).total_seconds() / 3600
    return max(0, horas_restantes)
