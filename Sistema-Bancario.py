from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    @staticmethod
    def filtrar_cliente(cpf, clientes):
        return next((cliente for cliente in clientes if cliente.cpf == cpf), None)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._cliente = cliente
        self._agencia = '0001'
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        self._saldo = valor

    @property
    def numero(self):
        return self._numero
    
    @numero.setter
    def numero(self, valor):
        self._numero = valor

    @property
    def agencia(self):
        return self._agencia
    
    @agencia.setter
    def agencia(self, valor):
        self._agencia = valor

    @property
    def cliente(self):
        return self._cliente
    
    @cliente.setter
    def cliente(self, valor):
        self._cliente = valor

    @property
    def historico(self):
        return self._historico

    @historico.setter
    def historico(self, valor):
        self._historico = valor

    def sacar(self, valor):
        if 0 < valor <= self.saldo:
            self.saldo -= valor
            print("\n === Saque realizado com sucesso! ===")
            return True
        exibir_mensagem("O saque falhou, saldo insuficiente ou valor inválido")
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            print("\n === Depósito realizado com sucesso! ===")
            return True
        exibir_mensagem("O valor informado é inválido")
        return False
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes 
                                       if transacao["tipo"] == Saque.__name__])
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            exibir_mensagem("O valor do saque excede o limite!")
        elif excedeu_saques:
            exibir_mensagem("Número máximo de saques excedido!")
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self) -> str:
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t{self.numero}
            Cliente:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    
    @classmethod
    @abstractmethod
    def registrar(cls, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def exibir_mensagem(mensagem):
    print(f"\n@@@ {mensagem} @@@")

def menu():
    menu = """\n
    ============ MENU ============
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

def buscar_cliente(clientes):
    cpf = input("Informe o CPF do cliente: ")
    return Cliente.filtrar_cliente(cpf, clientes)

def depositar(clientes):
    cliente = buscar_cliente(clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cliente = buscar_cliente(clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    conta = recuperar_conta_cliente(cliente)
    if conta:
        cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cliente = buscar_cliente(clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if conta:
        print("\n=============== EXTRATO ===============")
        transacoes = conta.historico.transacoes
        extrato = ""
        if not transacoes:
            extrato = "Não foram realizadas movimentações."
        else:
            for transacao in transacoes:
                extrato += f"\n{transacao['tipo']}:\n\tR${transacao['valor']:.2f}"
        print(extrato)
        print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
        print("=========================================")

def criar_cliente(clientes):
    cpf = input("Informe o CPF(somente números): ")
    cliente = Cliente.filtrar_cliente(cpf, clientes)
    if cliente:
        exibir_mensagem("Já existe um usuário com esse CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nasc = input("Informe uma data de nascimento (dd-mm-aaaa): ")
    end = input("Informe o endereco (Logradouro, nro - bairro - cidade/UF): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nasc, cpf=cpf, endereco=end)
    clientes.append(cliente)
    print("=== Usuário criado com sucesso! ===")

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        exibir_mensagem("Cliente não possui contas!")
        return None

    if len(cliente.contas) == 1:
        return cliente.contas[0]

    print("Selecione a conta:")
    for i, conta in enumerate(cliente.contas, start=1):
        print(f"{i}: Conta {conta.numero}")

    index = int(input("Informe o número da conta: ")) - 1
    return cliente.contas[index] if 0 <= index < len(cliente.contas) else None

def criar_conta(numero_conta, clientes, contas):
    cliente = buscar_cliente(clientes)
    if not cliente:
        exibir_mensagem("Cliente não encontrado! Fluxo de criação de conta encerrado.")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    for conta in contas:
        print("." * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()
        if opcao == "d":
            depositar(clientes)
        elif opcao == "s":
            sacar(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break
        else:
            print("Opção inválida, por favor selecionar novamente a operação desejada.")

main()