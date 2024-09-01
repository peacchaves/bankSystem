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


def depositar(saldo_atual, extrato_movimentacoes, valor_deposito, transacoes_realizadas, fuso_horario, /):
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


def sacar(*, saldo_atual, extrato_movimentacoes, valor_saque, limite_saque, saques_realizados, limite_saques_diarios,
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


def mostrar_extrato(saldo_atual, *, extrato):
    print("\n================ EXTRATO ================")
    if extrato:
        for movimentacao in extrato:
            print(movimentacao)
    else:
        print("Não foram realizadas movimentações.")
    print(f"\nSaldo atual: R$ {saldo_atual:.2f}")
    print("==========================================")


def criar_usuario(usuarios):
    while True:
        nome = input("Informe o nome: ").strip()
        if nome:
            break
        print("O nome do usuário não pode estar vazio.")

    while True:
        cpf = input("Informe o CPF (somente números): ").strip()
        if cpf.isdigit() and len(cpf) == 11 and cpf not in [u['cpf'] for u in usuarios]:
            break
        print("CPF inválido ou já cadastrado. Certifique-se de que contém 11 dígitos.")

    while True:
        data_nascimento = input("Informe a data de nascimento (DD/MM/AAAA): ").strip()
        try:
            datetime.strptime(data_nascimento, "%d/%m/%Y")
            break
        except ValueError:
            print("Data de nascimento inválida. Use o formato DD/MM/AAAA.")

    logradouro = input("Informe o logradouro, número e bairro: ").strip()
    while True:
        cep = input("Informe o CEP (somente números): ").strip()
        if cep.isdigit() and len(cep) == 8:
            break
        print("CEP inválido. Certifique-se de que contém 8 dígitos.")

    cidade = input("Informe a cidade: ").strip()
    while True:
        estado = input("Informe o estado (2 letras): ").strip().upper()
        if len(estado) == 2 and estado.isalpha():
            break
        print("Estado inválido. Informe apenas as duas letras.")

    usuario = {'nome': nome, 'cpf': cpf, 'data_nascimento': data_nascimento,
               'endereco': {'logradouro': logradouro, 'cep': cep, 'cidade': cidade, 'estado': estado}}
    usuarios.append(usuario)
    print(f"Usuário {nome} criado com sucesso.")


def criar_conta_corrente(contas, usuarios):
    if not usuarios:
        print("Nenhum usuário encontrado. Crie um usuário primeiro.")
        return

    cpf = input("Informe o CPF do usuário: ").strip()
    usuario = next((u for u in usuarios if u['cpf'] == cpf), None)
    if not usuario:
        print("Usuário não encontrado.")
        return

    numero_conta = len(contas) + 1
    conta = {'agencia': '0001', 'numero': numero_conta, 'usuario': usuario}
    contas.append(conta)
    print(f"Conta corrente {numero_conta} criada para o usuário {usuario['nome']}.")


def identificar_usuario(usuarios):
    cpf = input("Informe o CPF: ").strip()
    usuario = next((u for u in usuarios if u['cpf'] == cpf), None)
    if not usuario:
        raise ValorInvalidoError("CPF não encontrado.")
    return usuario


def listar_contas_usuario(usuario, contas):
    contas_usuario = [c for c in contas if c['usuario'] == usuario]
    if len(contas_usuario) == 1:
        return contas_usuario[0]
    elif contas_usuario:
        print("Escolha uma conta para acessar:")
        for idx, conta in enumerate(contas_usuario, 1):
            print(f"[{idx}] Agência: {conta['agencia']}, Conta: {conta['numero']}")
        while True:
            escolha = input("Digite o número da conta desejada: ")
            if escolha.isdigit() and 1 <= int(escolha) <= len(contas_usuario):
                return contas_usuario[int(escolha) - 1]
            print("Escolha inválida. Tente novamente.")
    else:
        print("Nenhuma conta encontrada para o usuário.")
        return None


def verificar_limite_transacoes(hora_ultima_transacao, fuso_horario):
    agora = datetime.now(fuso_horario)
    proxima_meia_noite = (hora_ultima_transacao + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    segundos_restantes = (proxima_meia_noite - agora).total_seconds()
    horas_restantes = int(segundos_restantes // 3600)
    minutos_restantes = int((segundos_restantes % 3600) // 60)
    return max(0, horas_restantes), max(0, minutos_restantes)
