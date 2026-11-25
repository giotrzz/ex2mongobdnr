import os
from datetime import date
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = os.getenv("MONGO_URI") or input("URI do MongoDB: ")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.mercado_livre


# =================================================================================
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
    produto = db.produto.find_one({"titulo": titulo})
    if not produto:
        print("Produto não encontrado.")
        return
    fav = {"titulo": produto["titulo"], "preco": produto["preco"],
           "vendedor": produto["vendedor"]["nome"]}
    r = db.usuario.update_one(
        {"nome": nome, "favoritos.titulo": {"$ne": titulo}},
        {"$push": {"favoritos": fav}})
    print("Favorito adicionado." if r.modified_count else "Usuário não encontrado ou já é favorito.")

def remove_favorito(nome, titulo):
    r = db.usuario.update_one({"nome": nome}, {"$pull": {"favoritos": {"titulo": titulo}}})
    print("Favorito removido." if r.modified_count else "Nada removido.")

def read_favoritos(nome):
    usuario = db.usuario.find_one({"nome": nome})
    if not usuario:
        print("Usuário não encontrado.")
        return
    print("Favoritos de", nome)
    for p in usuario.get("favoritos", []):
        print(p["titulo"], p["preco"], "- vendedor:", p["vendedor"])

# =====================================================================
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
    mydoc = {"nome": nome, "usuario": {"nome": usuario["nome"], "email": usuario["email"]}}
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
        print(x["nome"], "- dono:", x["usuario"]["nome"])

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


# ===================================================================================
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
    mydoc = {"titulo": titulo, "preco": preco, "vendedor": {"nome": vendedor["nome"]}}
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
        print(x["titulo"], x["preco"], "- vendedor:", x["vendedor"]["nome"])

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


# =========================================================================================
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
                    "titulo": produto["titulo"],
                    "quantidade": qtd,
                    "preco_unitario": produto["preco"],
                    "vendedor": produto["vendedor"]["nome"]
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
        "comprador": {"nome": comprador["nome"], "email": comprador["email"], "cpf": comprador["cpf"]},
        "endereco_entrega": comprador["enderecos"][0] if comprador.get("enderecos") else None,
        "data_pedido": date.today().isoformat(),
        "status": "Pendente",
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
        print("\nID:", x["_id"])
        print(x["data_pedido"], x["status"], x["valor_total"], "- comprador:", x["comprador"]["nome"])
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