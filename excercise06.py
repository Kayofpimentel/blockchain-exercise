import json
import pickle


def escrita(dados=[], nome_arquivo='05.txt', tipo='0'):
    dados.append(input('Valor escrita'))
    if tipo == '1':
        with open(nome_arquivo, mode='wb+') as arquivo:
            arquivo.seek(0)
            arquivo.write(pickle.dumps(dados))
            return True
    elif tipo == '2':
        with open(nome_arquivo, mode='w+') as arquivo:
            arquivo.seek(0)
            arquivo.write(json.dumps(dados))
            return True
    else:
        return False


def leitura(nome_arquivo='05.txt', tipo='0'):
    if tipo == '1':
        with open(nome_arquivo, mode='ab+') as arquivo:
            arquivo.seek(0)
            if arquivo.read(1):
                arquivo.seek(0)
                lista_dados = pickle.loads(arquivo.read())
                return lista_dados
    elif tipo == '2':
        with open(nome_arquivo, mode='a+') as arquivo:
            arquivo.seek(0)
            if arquivo.read(1):
                arquivo.seek(0)
                lista_dados = json.loads(arquivo.read())
                return lista_dados
    else:
        return None


to_run = True
dados = ['Oi', 'Teste']
while to_run:
    api = input('1 - Para pickle \n2 para json \n')
    operacao = input('1 - Escrever \n2 - Ler \n3 - Sair')
    if operacao == '1':
        dados = escrita(dados=dados, nome_arquivo='05.txt', tipo=api)
    elif operacao == '2':
        dados = leitura(nome_arquivo='05.txt', tipo=api)
        print(dados)
    else:
        to_run = False
    print('Operação bem sucedida')

print('Acabou')
