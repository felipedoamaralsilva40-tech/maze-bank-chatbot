nome = input('Digite o seu nome: ')

# CPF (11 números)
cpf = input('Digite seu CPF (somente números): ')
while not (cpf.isdigit() and len(cpf) == 11):
    cpf = input('CPF inválido. Digite exatamente 11 números: ')

# Data de nascimento (formato simples)
data_nascimento = input('Digite sua data de nascimento (dd/mm/aaaa): ')
while len(data_nascimento) != 10 or data_nascimento[2] != '/' or data_nascimento[5] != '/':
    data_nascimento = input('Data inválida. Use o formato dd/mm/aaaa: ')

# Senha + confirmação
senha = input('Crie uma senha: ')
confirmar_senha = input('Confirme a senha: ')

while senha != confirmar_senha:
    print('As senhas não coincidem!')
    senha = input('Crie uma senha: ')
    confirmar_senha = input('Confirme a senha: ')

# Profissão
profissao = input('Digite sua profissão: ')

# Email com @
email = input('Digite seu email: ')
while '@gmail.com' not in email:
    email = input('Email inválido. Deve conter "@gmail.com": ')

# Telefone (somente números)
telefone = input('Digite seu telefone (somente números): ')
while not telefone.isdigit():
    telefone = input('Telefone inválido. Digite apenas números: ')

print('\nCadastro realizado com sucesso!')
