import requests as req
from bs4 import BeautifulSoup as bs
import time
from selenium import webdriver as wb
import base64

class SiteVendaSeminovos:

    def __init__(self, url, emprise_name):
        self.__base_url = url
        self.__page_index = 1
        self.__emprise_name = emprise_name
        self.__soup = None

    def goto_next_page(self):
        self.__page_index += 1

    @property
    def base_url(self):
        return self.__base_url

    @property
    def page_index(self):
        return self.__page_index

    @property
    def soup(self):
        return self.__soup

    def set_soup(self):
        r = req.get(self.__base_url.format(self.__page_index))
        self.__soup = bs(r.text, "lxml")

    def is_finished(self):
        pass

    def get_cars(self):
        pass

    @property
    def emprise_name(self):
        return self.__emprise_name

    def get_price(self, car):
        pass

    def get_kilometragem(self, car):
        pass

    def get_model(self, car):
        pass

    def get_year(self, car):
        pass


class Movidas(SiteVendaSeminovos):

    def __init__(self, url, emprise_name):
        super().__init__(url, emprise_name)

    def is_finished(self):
        return self.soup.find_all(class_="nm-not-found-message")

    def get_cars(self):
        time.sleep(1.2)
        return [list(car.stripped_strings) for car in self.soup.find_all(class_="nm-product-info")]

    def get_year(self, car):
        return car[4]

    def get_kilometragem(self, car):
        return car[2]

    def get_model(self, car):
        return car[0]

    def get_price(self, car):
        return car[1][3:].replace(".", "").replace(",", ".")


class Unidas(SiteVendaSeminovos):

    def __init__(self, url, emprise_name):
        super().__init__(url, emprise_name)

    def is_finished(self):
        pagina_atual = list(self.soup.find(class_="active number").stripped_strings)[0]
        return self.page_index >= 2 and pagina_atual == '1'

    def get_cars(self):
        list1 = self.soup.find_all(class_="vehicleDescription")
        list2 = self.soup.find_all(class_="valor")
        return [(price, list(car.stripped_strings)) for car, price in zip(list1, list2)]

    def get_year(self, car):
        return car[1][3][-5:-1]

    def get_kilometragem(self, car):
        return car[1][4].split(",")[1][5:]

    def get_model(self, car):
        return car[1][2]

    def get_price(self, car):
        return car[0].text.replace(".", "").replace(",", ".")


class Localiza(SiteVendaSeminovos):
    def __init__(self, url, emprise_name):
        super().__init__(url, emprise_name)
        #self.__web_driver = wb.Chrome("/home/rafa/Documentos/web-scrap/chromedriver")
        self.__web_driver = wb.PhantomJS("/home/rafa/Documentos/web-scrap/phantomjs")
        self.__web_driver.get(url)
        self.__id_next_page = "ctl00_ctl42_g_f221d036_75d3_4ee2_893d_0d7b40180245_ProximaPaginaSuperior"
        self.__finished = False

    def set_soup(self):
        self.__soup = bs(self.__web_driver.page_source, "lxml")

    def is_finished(self):
        return self.__finished

    def get_cars(self):
        price = self.__soup.find_all(class_="busca-right-container")
        cars = self.__soup.find_all(class_="busca-left-container")
        return [(price, list(car.stripped_strings)) for car, price in zip(cars, price)]

    def get_year(self, car):
        return car[1][1].split("/")[0]

    def get_kilometragem(self, car):
        return car[1][2]

    def get_model(self, car):
        return car[1][0]

    def get_price(self, car):
        return list(car[0].stripped_strings)[0][3:].replace(".", "")

    def goto_next_page(self):
        try:
            self.__web_driver.find_element_by_id(self.__id_next_page).click()
        except:
            self.__finished = True


class Locamerica(SiteVendaSeminovos):
    def __init__(self, url, emprise_name):
        super().__init__(url, emprise_name)

    def set_soup(self):
        r = req.get(self.base_url.format(self.page_index))
        info = r.json()['veiculos']
        site_decoded = base64.b64decode(info)
        self.__soup = bs(site_decoded, "lxml")

    def is_finished(self):
        return not self.__soup.find(class_="clearfix")

    def get_cars(self):
        list1 = self.__soup.find_all(class_="item-carro")
        list2 = self.__soup.findAll(class_="preco")

        return [(list(car.stripped_strings), price) for car, price in zip(list1, list2)]

    def get_year(self, car):
        return car[0][3].split("/")[0]

    def get_kilometragem(self, car):
        kilometragem = car[0][7].split()[0]
        if kilometragem.count(".") > 1:  # maior que 1000 KMs
            kilometragem = kilometragem.replace(".", "", 1)  # tira o primeiro "."
        if kilometragem == '-':
            return 0
        else:
            return kilometragem

    def get_model(self, car):
        return car[0][1]

    def get_price(self, car):
        #print(car[1].h4.text)
        return car[1].h4.text.replace(".", "").replace(",", ".")

