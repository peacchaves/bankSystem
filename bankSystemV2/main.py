import pytz
from functions import (depositar, sacar, mostrar_extrato, identificar_usuario,
                       SaldoInsuficienteError, LimiteSaqueExcedidoError,
                       LimiteSaquesDiariosError, ValorInvalidoError, LimiteTransacoesDiariasError,
                       verificar_limite_transacoes, criar_usuario, criar_conta_corrente, listar_contas_usuario)

usuarios = []
contas = []

fuso_horario = pytz.timezone('America/Sao_Paulo')


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
            criar_usuario(usuarios)
        elif opcao == '2':
            criar_conta_corrente(contas, usuarios)
        elif opcao == '3':
            usuario = login(usuarios)
            if usuario:
                conta = listar_contas_usuario(usuario, contas)
                if conta:
                    menu_usuario(usuario, conta)
        elif opcao == 'q':
            print("Encerrando o sistema. Obrigado por usar nosso banco!")
            break
        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")


def login(usuarios):
    tentativas = 0
    while tentativas < 3:
        try:
            usuario = identificar_usuario(usuarios)
            return usuario
        except ValorInvalidoError as e:
            print(e)
            tentativas += 1
            print(f"Tentativa {tentativas} de 3.")

    print("Número máximo de tentativas excedido. Retornando ao menu principal.")
    return None


def menu_usuario(usuario, conta):
    saldo_atual = 0.0
    limite_saque = 500.0
    extrato_movimentacoes = []
    saques_realizados = 0
    limite_saques_diarios = 3
    transacoes_realizadas = 0
    limite_transacoes_diarias = 10
    hora_ultima_transacao = None

    menu = f"""
Olá, {usuario['nome']}! Você está acessando a Conta: {conta['numero']}
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
                    horas_restantes, minutos_restantes = verificar_limite_transacoes(hora_ultima_transacao,
                                                                                     fuso_horario)
                    if horas_restantes > 0 or minutos_restantes > 0:
                        print(
                            f"Limite de transações diárias atingido. Você poderá realizar transações novamente em {horas_restantes}h {minutos_restantes}min.")
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
                    horas_restantes, minutos_restantes = verificar_limite_transacoes(hora_ultima_transacao,
                                                                                     fuso_horario)
                    if horas_restantes > 0 or minutos_restantes > 0:
                        print(
                            f"Limite de transações diárias atingido. Você poderá sacar novamente em {horas_restantes}h {minutos_restantes}min.")
                        continue
                    else:
                        transacoes_realizadas = 0

                if saques_realizados >= limite_saques_diarios:
                    horas_restantes, minutos_restantes = verificar_limite_transacoes(hora_ultima_transacao,
                                                                                     fuso_horario)
                    if horas_restantes > 0 or minutos_restantes > 0:
                        print(
                            f"Limite de saques diários atingido. Você poderá sacar novamente em {horas_restantes}h {minutos_restantes}min.")
                        continue

                valor_saque = float(input("Informe o valor do saque: "))
                saldo_atual, extrato_movimentacoes, saques_realizados, transacoes_realizadas, hora_ultima_transacao = sacar(
                    saldo_atual=saldo_atual, extrato_movimentacoes=extrato_movimentacoes, valor_saque=valor_saque,
                    limite_saque=limite_saque, saques_realizados=saques_realizados,
                    limite_saques_diarios=limite_saques_diarios, transacoes_realizadas=transacoes_realizadas,
                    fuso_horario=fuso_horario)
            except (SaldoInsuficienteError, LimiteSaqueExcedidoError, LimiteSaquesDiariosError, ValorInvalidoError,
                    LimiteTransacoesDiariasError) as e:
                print(e)

        elif opcao == 'e':
            mostrar_extrato(saldo_atual, extrato=extrato_movimentacoes)

        elif opcao == 'q':
            print("Encerrando o sistema. Obrigado por usar nosso banco!")
            break

        else:
            print("Opção inválida. Por favor, escolha uma das opções disponíveis.")


menu_principal()
