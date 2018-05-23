from classes import *
import sqlite3 as sqlt
import json


with sqlt.connect("seminovos.db") as con:

    logs = open("arquivo_logs.txt", "a")
    log = """Data: {}\nEmpresa: {}\nTempo em segundos: {}\nQuantidade de carros: {}\n\n"""

    strings_queries = json.load(open("urls_queries.json"))
    criar_tabela_sql = strings_queries["criar_tabela_sql"]
    inserir_dados_sql = strings_queries["inserir_dados_sql"]
    cursor = con.cursor()
    cursor.execute(criar_tabela_sql)

    movidas = Movidas(strings_queries["url_movidas"], "Movidas")
    unidas = Unidas(strings_queries["url_unidas"], "Unidas")
    localiza = Localiza(strings_queries["url_localiza"], "Localiza")
    locamerica = Locamerica(strings_queries["url_locamerica"], "Locamerica")

    data = {}

    for seller_site in [locamerica, unidas, movidas, localiza]:
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

        tamanho_final = len(cursor.execute("select * from vendas").fetchall()) - tamanho_inicio_tabela
        dia_horario = time.asctime()

        logs.write(log.format(dia_horario, seller_site.emprise_name, int(time.time() - inicio_tempo), tamanho_final))
    logs.close()
