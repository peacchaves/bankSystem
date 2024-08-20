menu = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldoAtual = 0.0
limiteSaque = 500.0
extratoMovimentacoes = []
saquesRealizados = 0
limiteSaquesDiarios = 3

while True:
    opcao = input(menu).lower()

    if opcao == 'd':
        valorDeposito = float(input("Informe o valor do depósito: "))

        if valorDeposito > 0:
            saldoAtual += valorDeposito
            extratoMovimentacoes.append(f"Depósito: R$ {valorDeposito:.2f}")
        else:
            print("Depósito falhou! O valor deve ser positivo.")

    elif opcao == 's':
        valorSaque = float(input("Informe o valor do saque: "))

        if valorSaque > saldoAtual:
            print("Saque falhou! Saldo insuficiente.")
        elif valorSaque > limiteSaque:
            print("Saque falhou! O valor máximo por saque é R$ 500,00.")
        elif saquesRealizados >= limiteSaquesDiarios:
            print("Saque falhou! Limite de 3 saques diários atingido.")
        elif valorSaque > 0:
            saldoAtual -= valorSaque
            extratoMovimentacoes.append(f"Saque: R$ {valorSaque:.2f}")
            saquesRealizados += 1
        else:
            print("Saque falhou! O valor deve ser positivo.")

    elif opcao == 'e':
        print("\n================ EXTRATO ================")
        if extratoMovimentacoes:
            for movimentacao in extratoMovimentacoes:
                print(movimentacao)
        else:
            print("Não foram realizadas movimentações.")
        print(f"\nSaldo atual: R$ {saldoAtual:.2f}")
        print("==========================================")

    elif opcao == 'q':
        print("Encerrando o sistema. Obrigado por usar nosso banco!")
        break

    else:
        print("Opção inválida. Por favor, escolha uma das opções disponíveis.")