from classes import *
import sqlite3 as sqlt


with sqlt.connect("seminovos2.db") as con:
    cursor = con.cursor()
    criar_tabela_sql = """CREATE TABLE vendas 
    (  
     ID INTEGER PRIMARY KEY AUTOINCREMENT,  
     Empresa VARCHAR (20) NOT NULL,  
     Modelo  VARCHAR(40) NOT NULL,  
     Preco REAL NOT NULL,
     Kilometragem REAL NOT NULL,
     Ano NUMERIC(4,0) NOT NULL
    );"""

    cursor.execute(criar_tabela_sql)

    inserir_dados_sql = """
    INSERT INTO vendas (Empresa, Modelo, Preco, Kilometragem, Ano) 
    VALUES ("{Empresa}","{Modelo}", {Preco},{Kilometragem},{Ano})
    """

    url_movidas = "https://busca.movidaseminovos.com.br/filtros/class/usado?sort=11&page={}"
    url_unidas = "https://www.seminovosunidas.com.br/veiculos/page:{}?" + \
                 "utm_source=afilio&utm_medium=display&utm_campaign=maio&utm_content" + \
                 "=ron_ambos&utm_term=120x600_promocaomaio_performance_-_-"

    movidas = Movidas(url_movidas, "Movidas")
    unidas = Unidas(url_unidas, "Unidas")

    data = {}

    for seller_site in [unidas, movidas]:
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
            seller_site.next_page()

