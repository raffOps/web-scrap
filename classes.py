import requests as req
from bs4 import BeautifulSoup as bs
import time
from selenium import webdriver as wb
import base64
import os
from inspect import getmembers, isfunction


class Docstring:
    """
    Decorador de classe que possibilita que uma classe herde a docstring da sua classe pai
    """
    @staticmethod
    def inherit_docstring_from_superclass(cls):
        """
        Dado uma classe, copia os docstrings dos metodos da classe pai para os metodos desta classe que nao possuem
        docstrings
        :param cls: Uma classe qualquer
        :return: A classe com os docstrings dos seus metodos herdados dos docstrings da classe pai
        """
        for name, func in getmembers(cls, isfunction):
            if func.__doc__: continue
            for parent in cls.__mro__[1:]:
                if hasattr(parent, name):
                    func.__doc__ = getattr(parent, name).__doc__
        return cls


class SiteVendaSeminovos:
    """
    Classe pai da classes de web-scrap de cada site. Alguns metodos sao abstratos.
    """

    def __init__(self, url, emprise_name):
        """
        :param url: a url com a qual o web-scrap da pagina irá ser iniciado. As urls sao depositadas no
                    arquivo urls_queries.json
        :param emprise_name: o nome da empresa
        """
        self.__base_url = url
        self.__page_index = 1 #As urls de Movidas, Unidas e Locamerica possuem um indice de pagina nas suas urls
        self.__emprise_name = emprise_name
        self.__soup = None

    @property
    def base_url(self):
        """
        Retorna a url atual onde esta acontecendo o scrap
        :return: A url atual do objeto
        :rtype: str
        """
        return self.__base_url

    @property
    def page_index(self):
        """
        Retorna o index da pagina de onde está acontecendo o scrap
        :return: O index da pagina
        :rtype: int
        """
        return self.__page_index

    @property
    def soup(self):
        """
        Retorna o HTML da pagina de onde está acontecendo o scrap
        :return: O HTML da pagina
        :rtype: bs4.BeautifulSoup
        """
        return self.__soup

    def goto_next_page(self):
        """
        Itera as paginas de um site
        """
        self.__page_index += 1

    def set_soup(self):
        """
        Seta o html de uma pagina
        """
        r = req.get(self.__base_url.format(self.__page_index))
        self.__soup = bs(r.text, "lxml")

    def is_finished(self):
        """
        Verifica se chegou ao fim a iteracao das paginas do site
        :return: True se chegou ao fim a iterecao, False caso o contrario
        :rtype: bool
        """
        pass

    def get_cars(self):
        """
        Extrai do html da pagina uma tupla contendo os dados crus de cada carro presente na pagina
        :return: Tupla contendo os dados crus de cada carro presente na pagina
        :rtype: tuple
        """
        pass

    @property
    def emprise_name(self):
        """
        Retorna a kilometragem do carro
        :return: kilometragem do carro
        :rtype: int
        """
        return self.__emprise_name

    def get_price(self, car):
        """
        Dado uma tupla de strings contendo os dados de um carro, retorna o preco do carro
        :param car: Tupla de strings contendo os dados de um carro
        :type car: tuple
        :return: preco do carro
        :rtype: float
        """
        pass

    def get_kilometragem(self, car):
        """
        Dado uma tupla de strings contendo os dados de um carro, retorna a kilometragem do carro
        :param car: Tupla de strings contendo os dados de um carro
        :type car: tuple
        :return: kilometragem do carro
        :rtype: int
        """
        pass

    def get_model(self, car):
        """
        Dado uma tupla de strings contendo os dados de um carro, retorna o modelo do carro
        :param car: Tupla de strings contendo os dados de um carro
        :type car: tuple
        :return: Modelo do carro
        :rtype: str
        """
        pass

    def get_year(self, car):
        """
        Dado uma tupla de strings contendo os dados de um carro, retorna o ano de fabricacao do carro
        :param car: tuple
        :return: Ano de fabricacao do carro
        :rtype: int
        """
        pass


@Docstring.inherit_docstring_from_superclass
class Movidas(SiteVendaSeminovos):
    """
    Classe para extracao dos dados do site da Movidas
    """

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


@Docstring.inherit_docstring_from_superclass
class Unidas(SiteVendaSeminovos):
    """
    Classe para extracao dos dados do site da Unidas
    """
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


@Docstring.inherit_docstring_from_superclass
class Localiza(SiteVendaSeminovos):
    """
    Classe para extracao dos dados do site da Localiza. A iteracao das paginas do site acontece via javascript,
    por isso a utilizacao do selenium nessa classe
    """
    def __init__(self, url, emprise_name):
        super().__init__(url, emprise_name)
        self.__web_driver = wb.Chrome(os.path.abspath("chromedriver.exe"))
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


@Docstring.inherit_docstring_from_superclass
class Locamerica(SiteVendaSeminovos):
    """
    Classe para extracao dos dados do site da Locamerica
    """
    def __init__(self, url, emprise_name):
        super().__init__(url, emprise_name)

    def set_soup(self):
        r = req.get(self.base_url.format(self.page_index))
        info = r.json()['veiculos'] # os dados dos carros da Locamerica estao numa requisicao json, nao no HTML
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
        return car[1].h4.text.replace(".", "").replace(",", ".")

