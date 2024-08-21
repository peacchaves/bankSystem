class SaldoInsuficienteError(Exception):
    pass


class LimiteSaqueExcedidoError(Exception):
    pass


class LimiteSaquesDiariosError(Exception):
    pass


class ValorInvalidoError(Exception):
    pass


def depositar(saldo_atual, extrato_movimentacoes, valor_deposito):
    if valor_deposito <= 0:
        raise ValorInvalidoError("O valor do depósito deve ser positivo.")

    saldo_atual += valor_deposito
    extrato_movimentacoes.append(f"Depósito: R$ {valor_deposito:.2f}")
    print(f"Depósito de R$ {valor_deposito:.2f} realizado com sucesso!")
    return saldo_atual, extrato_movimentacoes


def sacar(saldo_atual, extrato_movimentacoes, valor_saque, limite_saque, saques_realizados, limite_saques_diarios):
    if valor_saque > saldo_atual:
        raise SaldoInsuficienteError("Saldo insuficiente para realizar o saque.")
    if valor_saque > limite_saque:
        raise LimiteSaqueExcedidoError("O valor do saque excede o limite permitido.")
    if saques_realizados >= limite_saques_diarios:
        raise LimiteSaquesDiariosError("Limite de saques diários atingido.")
    if valor_saque <= 0:
        raise ValorInvalidoError("O valor do saque deve ser positivo.")

    saldo_atual -= valor_saque
    extrato_movimentacoes.append(f"Saque: R$ {valor_saque:.2f}")
    saques_realizados += 1
    print(f"Saque de R$ {valor_saque:.2f} realizado com sucesso!")
    return saldo_atual, extrato_movimentacoes, saques_realizados


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
