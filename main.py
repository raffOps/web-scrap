from classes import *
import sqlite3 as sqlt
import json


with sqlt.connect("seminovos.db") as con:

    # Abertura do arquivo json que contém as urls dos sites e as consultas SQL
    strings_queries = json.load(open("urls_queries.json"))

    # Criacao da tabela "vendas"
    criar_tabela_sql = strings_queries["criar_tabela_sql"]
    inserir_dados_sql = strings_queries["inserir_dados_sql"]
    cursor = con.cursor()
    cursor.execute(strings_queries["eliminar_tabela_se_existe"])
    cursor.execute(criar_tabela_sql)

    # Instanciação de cada uma das classes dos sites
    movidas = Movidas(strings_queries["url_movidas"], "Movidas")
    unidas = Unidas(strings_queries["url_unidas"], "Unidas")
    localiza = Localiza(strings_queries["url_localiza"], "Localiza")
    locamerica = Locamerica(strings_queries["url_locamerica"], "Locamerica")

    data = {}

    # Para cada página de cada site, extrai os dados e insere na tabela "vendas"
    for seller_site in [movidas, unidas, locamerica, localiza]:
        inicio_tempo = time.time()
        tamanho_inicio_tabela = len(cursor.execute("select * from vendas").fetchall())
        while True:
            seller_site.set_soup()
            if seller_site.is_finished():
                break
            for car in seller_site.get_cars():
                data["Empresa"] = seller_site.emprise_name
                data["Modelo"] = seller_site.get_model(car)
                data["Preco"] = seller_site.get_price(car)
                data["Kilometragem"] = seller_site.get_kilometragem(car)
                data["Ano"] = seller_site.get_year(car)
                cursor.execute(inserir_dados_sql.format(**data))
            con.commit()
            seller_site.goto_next_page()
