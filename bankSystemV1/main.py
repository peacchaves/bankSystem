import pytz

from functions import (depositar, sacar, mostrar_extrato, identificar_usuario,
                       SaldoInsuficienteError, LimiteSaqueExcedidoError,
                       LimiteSaquesDiariosError, ValorInvalidoError, LimiteTransacoesDiariasError,
                       verificar_limite_transacoes)

saldo_atual = 0.0
limite_saque = 500.0
extrato_movimentacoes = []
saques_realizados = 0
limite_saques_diarios = 3
transacoes_realizadas = 0
limite_transacoes_diarias = 10
hora_ultima_transacao = None

fuso_horario = pytz.timezone('America/Sao_Paulo')

while True:
    try:
        usuario = identificar_usuario()
        break
    except ValorInvalidoError as e:
        print(e)

menu = f"""
Olá, {usuario}!
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

while True:
    opcao = input(menu).lower()

    if opcao == 'd':
        try:
            if transacoes_realizadas >= limite_transacoes_diarias:
                horas_restantes = verificar_limite_transacoes(hora_ultima_transacao, fuso_horario)
                if horas_restantes > 0:
                    print(f"Limite de transações diárias atingido. Você poderá realizar transações novamente em {horas_restantes:.2f} horas.")
                    continue
                else:
                    transacoes_realizadas = 0

            valor_deposito = float(input("Informe o valor do depósito: "))
            saldo_atual, extrato_movimentacoes, transacoes_realizadas, hora_ultima_transacao = depositar(
                saldo_atual, extrato_movimentacoes, valor_deposito, transacoes_realizadas, fuso_horario)
        except ValorInvalidoError as e:
            print(e)

    elif opcao == 's':
        try:
            if transacoes_realizadas >= limite_transacoes_diarias:
                horas_restantes = verificar_limite_transacoes(hora_ultima_transacao, fuso_horario)
                if horas_restantes > 0:
                    print(f"Limite de transações diárias atingido. Você poderá realizar transações novamente em {horas_restantes:.2f} horas.")
                    continue
                else:
                    transacoes_realizadas = 0

            if saques_realizados >= limite_saques_diarios:
                horas_restantes = verificar_limite_transacoes(hora_ultima_transacao, fuso_horario)
                if horas_restantes > 0:
                    print(f"Limite de saques diários atingido. Você poderá sacar novamente em {horas_restantes:.2f} horas.")
                    continue

            valor_saque = float(input("Informe o valor do saque: "))
            saldo_atual, extrato_movimentacoes, saques_realizados, transacoes_realizadas, hora_ultima_transacao = sacar(
                saldo_atual, extrato_movimentacoes, valor_saque, limite_saque, saques_realizados, limite_saques_diarios, transacoes_realizadas, fuso_horario)
        except (SaldoInsuficienteError, LimiteSaqueExcedidoError, LimiteSaquesDiariosError, ValorInvalidoError, LimiteTransacoesDiariasError) as e:
            print(e)

    elif opcao == 'e':
        mostrar_extrato(extrato_movimentacoes, saldo_atual)

    elif opcao == 'q':
        print("Encerrando o sistema. Obrigado por usar nosso banco!")
        break

    else:
        print("Opção inválida. Por favor, escolha uma das opções disponíveis.")
