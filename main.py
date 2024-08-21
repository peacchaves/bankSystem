from functions import (depositar, sacar, mostrar_extrato, identificar_usuario,
                       SaldoInsuficienteError, LimiteSaqueExcedidoError,
                       LimiteSaquesDiariosError, ValorInvalidoError)

saldo_atual = 0.0
limite_saque = 500.0
extrato_movimentacoes = []
saques_realizados = 0
limite_saques_diarios = 3

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
            valor_deposito = float(input("Informe o valor do depósito: "))
            saldo_atual, extrato_movimentacoes = depositar(saldo_atual, extrato_movimentacoes, valor_deposito)
        except ValorInvalidoError as e:
            print(e)

    elif opcao == 's':
        try:
            valor_saque = float(input("Informe o valor do saque: "))
            saldo_atual, extrato_movimentacoes, saques_realizados = sacar(
                saldo_atual, extrato_movimentacoes, valor_saque, limite_saque, saques_realizados, limite_saques_diarios)
        except (SaldoInsuficienteError, LimiteSaqueExcedidoError, LimiteSaquesDiariosError, ValorInvalidoError) as e:
            print(e)

    elif opcao == 'e':
        mostrar_extrato(extrato_movimentacoes, saldo_atual)

    elif opcao == 'q':
        print("Encerrando o sistema. Obrigado por usar nosso banco!")
        break

    else:
        print("Opção inválida. Por favor, escolha uma das opções disponíveis.")
