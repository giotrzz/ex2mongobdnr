import os
from datetime import date
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = os.getenv("MONGO_URI") or input("URI do MongoDB: ")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.mercado_livre


# =============== USUÁRIO (nome, email, cpf, enderecos, favoritos) ===============
def create_usuario():
    #Insert
    mycol = db.usuario
    print("\nInserindo um novo usuário")
    nome = input("Nome: ")
    email = input("E-mail: ")
    cpf = input("CPF: ")
    key = 1
    end = []
    while (key != 'N'):
        rua = input("Rua: ")
        num = input("Num: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        estado = input("Estado: ")
        cep = input("CEP: ")
        endereco = {
            "rua": rua,
            "num": num,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        }
        end.append(endereco)
        key = input("Deseja cadastrar um novo endereço (S/N)? ").upper()
    mydoc = {"nome": nome, "email": email, "cpf": cpf, "enderecos": end, "favoritos": []}
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)

def read_usuario(nome):
    #Read
    mycol = db.usuario
    print("Usuários existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"], x.get("email"), x.get("cpf"))
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

def update_usuario(nome):
    #Update
    mycol = db.usuario
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if not mydoc:
        print("Usuário não encontrado.")
        return
    print("Dados do usuário: ", mydoc)
    novos = {}
    novo_nome = input("Mudar Nome:")
    if len(novo_nome):
        novos["nome"] = novo_nome
    email = input("Mudar E-mail:")
    if len(email):
        novos["email"] = email
    cpf = input("Mudar CPF:")
    if len(cpf):
        novos["cpf"] = cpf
    if novos:
        mycol.update_one(myquery, {"$set": novos})
    print("Usuário atualizado.")

def delete_usuario(nome):
    #Delete
    mycol = db.usuario
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletando o usuário ", mydoc)

def add_favorito(nome, titulo):
    usuario = db.usuario.find_one({"nome": nome})
    produto = db.produto.find_one({"titulo": titulo})
    if not usuario or not produto:
        print("Usuário ou produto não encontrado.")
        return
    db.usuario.update_one({"_id": usuario["_id"]}, {"$addToSet": {"favoritos": produto["_id"]}})
    print("Favorito adicionado.")

def remove_favorito(nome, titulo):
    usuario = db.usuario.find_one({"nome": nome})
    produto = db.produto.find_one({"titulo": titulo})
    if not usuario or not produto:
        print("Usuário ou produto não encontrado.")
        return
    db.usuario.update_one({"_id": usuario["_id"]}, {"$pull": {"favoritos": produto["_id"]}})
    print("Favorito removido.")

def read_favoritos(nome):
    usuario = db.usuario.find_one({"nome": nome})
    if not usuario:
        print("Usuário não encontrado.")
        return
    print("Favoritos de", nome)
    for p in db.produto.find({"_id": {"$in": usuario.get("favoritos", [])}}):
        print(p["titulo"], p["preco"])


# =============== VENDEDOR (nome, usuario_id) ===============
def create_vendedor():
    #Insert
    mycol = db.vendedor
    print("\nInserindo um novo vendedor")
    nome_usuario = input("Nome do usuário dono da conta: ")
    usuario = db.usuario.find_one({"nome": nome_usuario})
    if not usuario:
        print("Usuário não encontrado.")
        return
    nome = input("Nome do vendedor: ")
    mydoc = {"nome": nome, "usuario_id": usuario["_id"]}
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)

def read_vendedor(nome):
    #Read
    mycol = db.vendedor
    print("Vendedores existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
    else:
        mydoc = mycol.find({"nome": nome})
    for x in mydoc:
        dono = db.usuario.find_one({"_id": x["usuario_id"]})
        print(x["nome"], "- dono:", dono["nome"] if dono else "-")

def update_vendedor(nome):
    #Update
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if not mydoc:
        print("Vendedor não encontrado.")
        return
    print("Dados do vendedor: ", mydoc)
    novo_nome = input("Mudar Nome:")
    if len(novo_nome):
        mycol.update_one(myquery, {"$set": {"nome": novo_nome}})
    print("Vendedor atualizado.")

def delete_vendedor(nome):
    #Delete
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletando o vendedor ", mydoc)


# =============== PRODUTO (titulo, preco, vendedor_id) ===============
def create_produto():
    #Insert
    mycol = db.produto
    print("\nInserindo um novo produto")
    nome_vendedor = input("Nome do vendedor: ")
    vendedor = db.vendedor.find_one({"nome": nome_vendedor})
    if not vendedor:
        print("Vendedor não encontrado.")
        return
    titulo = input("Digite o produto a ser criado: ")
    try:
        preco = float(input("Digite o preço do produto: ").replace(",", "."))
    except ValueError:
        print("Preço inválido.")
        return
    mydoc = {"titulo": titulo, "preco": preco, "vendedor_id": vendedor["_id"]}
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)

def read_produto(titulo):
    #Read
    mycol = db.produto
    print("Produtos existentes: ")
    if not len(titulo):
        mydoc = mycol.find().sort("titulo")
    else:
        mydoc = mycol.find({"titulo": titulo})
    for x in mydoc:
        vendedor = db.vendedor.find_one({"_id": x["vendedor_id"]})
        print(x["titulo"], x["preco"], "- vendedor:", vendedor["nome"] if vendedor else "-")

def update_produto(titulo):
    #Update
    mycol = db.produto
    myquery = {"titulo": titulo}
    mydoc = mycol.find_one(myquery)
    if not mydoc:
        print("Produto não encontrado.")
        return
    print("Dados do produto: ", mydoc)
    novos = {}
    novo_titulo = input("Mudar Título:")
    if len(novo_titulo):
        novos["titulo"] = novo_titulo
    novo_preco = input("Mudar Preço:")
    if len(novo_preco):
        try:
            novos["preco"] = float(novo_preco.replace(",", "."))
        except ValueError:
            print("Preço inválido, mantendo o anterior.")
    if novos:
        mycol.update_one(myquery, {"$set": novos})
    print("Produto atualizado.")

def delete_produto(titulo):
    #Delete
    mycol = db.produto
    myquery = {"titulo": titulo}
    mydoc = mycol.delete_one(myquery)
    print("Deletando o produto ", mydoc)


# =============== COMPRA (comprador_id, data_pedido, status, valor_total, itens) ===============
def create_compra():
    #Insert
    mycol = db.compra
    print("\nInserindo uma nova compra")
    nome_comprador = input("Nome do comprador: ")
    comprador = db.usuario.find_one({"nome": nome_comprador})
    if not comprador:
        print("Usuário não encontrado.")
        return
    key = 1
    itens = []
    while (key != 'N'):
        titulo = input("Título do produto: ")
        produto = db.produto.find_one({"titulo": titulo})
        if produto:
            try:
                qtd = int(input("Quantidade: "))
                item = {
                    "produto_id": produto["_id"],
                    "titulo": produto["titulo"],
                    "quantidade": qtd,
                    "preco_unitario": produto["preco"]
                }
                itens.append(item)
            except ValueError:
                print("Quantidade inválida.")
        else:
            print("Produto não encontrado.")
        key = input("Adicionar outro item (S/N)? ").upper()
    if not itens:
        print("Compra sem itens, cancelada.")
        return
    valor_total = 0
    for i in itens:
        valor_total = valor_total + i["quantidade"] * i["preco_unitario"]
    mydoc = {
        "comprador_id": comprador["_id"],
        "data_pedido": date.today().isoformat(),
        "valor_total": round(valor_total, 2),
        "itens": itens
    }
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ", x.inserted_id)

def read_compra(status):
    #Read
    mycol = db.compra
    print("Compras existentes: ")
    if not len(status):
        mydoc = mycol.find()
    else:
        mydoc = mycol.find({"status": status})
    for x in mydoc:
        comprador = db.usuario.find_one({"_id": x["comprador_id"]})
        print("\nID:", x["_id"])
        print(x["data_pedido"], x["status"], x["valor_total"], "- comprador:", comprador["nome"] if comprador else "-")
        for i in x["itens"]:
            print("   ", i["quantidade"], "x", i["titulo"], i["preco_unitario"])

def update_compra(id_compra):
    #Update
    mycol = db.compra
    try:
        myquery = {"_id": ObjectId(id_compra)}
    except Exception:
        print("ID inválido.")
        return
    mydoc = mycol.find_one(myquery)
    if not mydoc:
        print("Compra não encontrada.")
        return
    print("Dados da compra: ", mydoc)
    novos = {}
    novo_status = input("Mudar Status:")
    if len(novo_status):
        novos["status"] = novo_status
    nova_data = input("Mudar Data:")
    if len(nova_data):
        novos["data_pedido"] = nova_data
    if novos:
        mycol.update_one(myquery, {"$set": novos})
    print("Compra atualizada.")

def delete_compra(id_compra):
    #Delete
    mycol = db.compra
    try:
        myquery = {"_id": ObjectId(id_compra)}
    except Exception:
        print("ID inválido.")
        return
    mydoc = mycol.delete_one(myquery)
    print("Deletando a compra ", mydoc)


# =============== MENU ===============
key = 0
sub = 0
while (key != 'S'):
    print("\n1-CRUD Usuário")
    print("2-CRUD Vendedor")
    print("3-CRUD Produto")
    print("4-CRUD Compra")
    key = input("Digite a opção desejada? (S para sair) ").upper()

    if (key == '1'):
        sub = 0
        while (sub != 'V'):
            print("\nMenu do Usuário")
            print("1-Create Usuário")
            print("2-Read Usuário")
            print("3-Update Usuário")
            print("4-Delete Usuário")
            print("5-Adicionar Favorito")
            print("6-Remover Favorito")
            print("7-Ver Favoritos")
            sub = input("Digite a opção desejada? (V para voltar) ").upper()
            if (sub == '1'):
                create_usuario()
            elif (sub == '2'):
                nome = input("Read usuário, deseja algum nome específico? ")
                read_usuario(nome)
            elif (sub == '3'):
                nome = input("Update usuário, qual nome? ")
                update_usuario(nome)
            elif (sub == '4'):
                nome = input("Nome a ser deletado: ")
                delete_usuario(nome)
            elif (sub == '5'):
                nome = input("Nome do usuário: ")
                titulo = input("Título do produto: ")
                add_favorito(nome, titulo)
            elif (sub == '6'):
                nome = input("Nome do usuário: ")
                titulo = input("Título do produto: ")
                remove_favorito(nome, titulo)
            elif (sub == '7'):
                nome = input("Nome do usuário: ")
                read_favoritos(nome)

    elif (key == '2'):
        sub = 0
        while (sub != 'V'):
            print("\nMenu do Vendedor")
            print("1-Create Vendedor")
            print("2-Read Vendedor")
            print("3-Update Vendedor")
            print("4-Delete Vendedor")
            sub = input("Digite a opção desejada? (V para voltar) ").upper()
            if (sub == '1'):
                create_vendedor()
            elif (sub == '2'):
                nome = input("Read vendedor, deseja algum nome específico? ")
                read_vendedor(nome)
            elif (sub == '3'):
                nome = input("Update vendedor, qual nome? ")
                update_vendedor(nome)
            elif (sub == '4'):
                nome = input("Nome a ser deletado: ")
                delete_vendedor(nome)

    elif (key == '3'):
        sub = 0
        while (sub != 'V'):
            print("\nMenu do Produto")
            print("1-Create Produto")
            print("2-Read Produto")
            print("3-Update Produto")
            print("4-Delete Produto")
            sub = input("Digite a opção desejada? (V para voltar) ").upper()
            if (sub == '1'):
                create_produto()
            elif (sub == '2'):
                titulo = input("Read produto, deseja algum título específico? ")
                read_produto(titulo)
            elif (sub == '3'):
                titulo = input("Update produto, qual título? ")
                update_produto(titulo)
            elif (sub == '4'):
                titulo = input("Título a ser deletado: ")
                delete_produto(titulo)

    elif (key == '4'):
        sub = 0
        while (sub != 'V'):
            print("\nMenu da Compra")
            print("1-Create Compra")
            print("2-Read Compra")
            print("3-Update Compra")
            print("4-Delete Compra")
            sub = input("Digite a opção desejada? (V para voltar) ").upper()
            if (sub == '1'):
                create_compra()
            elif (sub == '2'):
                status = input("Read compra, deseja algum status específico? ")
                read_compra(status)
            elif (sub == '3'):
                id_compra = input("Update compra, ID da compra: ")
                update_compra(id_compra)
            elif (sub == '4'):
                id_compra = input("ID da compra a ser deletada: ")
                delete_compra(id_compra)