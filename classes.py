import requests as req
from bs4 import BeautifulSoup as bs
import time


class SiteVendaSeminovos:

    def __init__(self, url, emprise_name):
        self.__base_url = url
        self.__page_index = 1
        self.__emprise_name = emprise_name
        self.__soup = None

    def next_page(self):
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




