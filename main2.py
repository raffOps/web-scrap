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
    url_localiza = "https://seminovos.localiza.com/Paginas/resultado-busca.aspx?ct=4365_2002_8466_8607_8655_4389_2604_2612_8096_1734_4720_8719_3970_7267_7300_2826_8146_5758_6667_565_8167_1307_2108_7478_8875_2372_6698_8220_4777_8234_3159_8987_6018_108_4498_9040_6057_9061_6974_6744_6749_9123_7690_9185_7719_5210_6797_957_9317_9328_9332_9352_7876_2453_9362_1968_9391_9420_5454_3873_3874_4337_1987_1081_6875&st=AL_BA_CE_DF_ES_GO_MA_MG_MS_MT_PA_PB_PE_PI_PR_RJ_RN_RS_SC_SE_SP&yr=2013_2018&pc=20000_425000&fb=W_X_T_%C3%94_A_D_C_L_1_8_F_M_U_O_R_G_B&md=000192_000097_000148_000147_000136_000119_000137_000120_000729_001061_000132_000632_000699_000122_000041_000286_000772_000719_000180_000181_000179_000715_000736_000854_000748_001076_000334_000250_000333_000330_000332_000369_000424_000545_000511_000488_000408_000418_000510_000513_000391_000211_000431_001083_000325_000326_000344_000456_000451_000455_000458_000505_000506_000502_000805_000426_000427_000623_000726_000718_000119_000132_000694_000788_000828_000005_000484_000478_000481_000476_000473_000477_001017_001016_000356_000357_000319_000317_000297_000298_000354_000123_000780_000859_000138_001006_000614_000867_000858_000675_000139_000165_000171_000174_000039_000020_000022_000019_000747_000320_000365_000311_000355_000312_000313_000322_000342_000353_000362_000314_000699_000696_000114_000779_000781_000755_000807_000806_001084_000529_001063_001098_000667_001036_001077_000133_000143_000658_000705_000707_000047"
    movidas = Movidas(url_movidas, "Movidas")
    unidas = Unidas(url_unidas, "Unidas")
    localiza = Localiza(url_localiza, "Localiza")

    data = {}

    for seller_site in [localiza]:
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

