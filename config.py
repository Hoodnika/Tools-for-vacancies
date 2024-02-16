import psycopg2
import requests
from abc import ABC
import json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class MixinFuncs(ABC):
    """
    Миксин класс для обязывания дочерних классов к определенным методам
    """

    @classmethod
    def get_companies_and_vacancies_count(cls):
        """

        :return: Получает список всех компаний и количество вакансий у каждой компании.
        """
        pass

    @classmethod
    def get_all_vacancies(cls):
        """

        :return: Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки
        на вакансию.
        """
        pass

    @classmethod
    def get_avg_salary(cls):
        """

        :return: Получает среднюю зарплату по вакансиям.
        """
        pass

    @classmethod
    def get_vacancies_with_higher_salary(cls):
        """

        :return: Плучает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        """
        pass

    @classmethod
    def get_vacancies_with_keyword(cls, text):
        """

        :return: Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например python.
        """
        pass


class StandartData:
    """
    Родительский класс для указания переменных и их инкапсуляции
    """

    def __init__(self):
        pass


class HH:
    """
    Класс для работы по API ключу с сайтом HH.ru
    """
    url_employers = 'https://api.hh.ru/employers'
    employer_page = 10  # изначально стоит 10 страница для не сильной нагруженности, можно изменить до 0
    vacancy_page = 0
    lst_exemplars = []

    @classmethod
    def get_employers(cls):
        """
        функция запроса по API для получения информации о работадателях
        :return:
        """
        vacancies = requests.get(HH.url_employers,
                                 params={
                                     'only_with_vacancies': True,
                                     'page': HH.employer_page,
                                     'sort_by': 'by_vacancies_open'}).json()
        return vacancies

    @classmethod
    def get_vacancies(cls, url):
        """
        функция запроска по API для получения информации о вакансиях
        :param url:
        :return:
        """
        vacancies_info = requests.get(url, params={'per_page': 100, 'page': HH.vacancy_page}).json()

        return vacancies_info

    @classmethod
    def return_info(cls, lst_dir):
        """
        Используется для отладки
        :return: словарь в удобном формате
        """
        return json.dumps(lst_dir, indent=2, ensure_ascii=False)

    @classmethod
    def employers_to_lstdir(cls):
        """
        функия получения списка работадателей по API, преобразования в нужный формат для дальнейшего добавления в
        файл COMPANIES.json
        :return: список словарей, где каждый словарь - работадатель с определенными данными о ней
        """
        lst_vacancies = []
        companies_items = cls.get_employers()

        for element in companies_items['items']:
            if int(element['open_vacancies']) > 0:
                company_to_add = {
                    'Company_name': element['name'],
                    'Company_id': element['id'],
                    'Open_vacancies': element['open_vacancies'],
                    'vacancies_url': element['vacancies_url']
                }
                lst_vacancies.append(company_to_add)

        return lst_vacancies

    def __init__(self, name, town, salary,
                 url_vacancy, company, snippet, id_vacancy, id_company, url_company):
        self.__name = name
        self.__town = town
        self.__salary = salary
        self.__url_vacancy = url_vacancy
        self.__company = company
        self.__snippet = snippet
        self.__id_vacancy = id_vacancy
        self.__id_company = id_company
        self.__url_company = url_company

    def __repr__(self):
        return f'{self.__name}'

    @property
    def name(self):
        return self.__name

    @property
    def town(self):
        return self.__town

    @property
    def salary(self):
        """
        фультрация ключа зарплаты в словаре API запроса
        :return:
        """
        if self.__salary is None:
            return self.__salary
        elif self.__salary['from'] is None:
            return self.__salary['to']
        elif self.__salary['to'] is None:
            return self.__salary['from']
        elif self.__salary['from'] and self.__salary['to'] is not None:
            return self.__salary['from']

    @property
    def url_vacancy(self):
        return self.__url_vacancy

    @property
    def company(self):
        return self.__company

    @property
    def snippet(self):
        return self.__snippet

    @property
    def id_vacancy(self):
        return self.__id_vacancy

    @property
    def id_company(self):
        return self.__id_company

    @property
    def url_company(self):
        return self.__url_company

    @classmethod
    def add_vacancies_exemplars(cls, url):
        """
        функция для инцилизации вакансий в экземляры класса HH, добавляет экземпляры в список lst_exemplars
        :param url: get запрос по API вакансий, получаемый из функции get_vacancies
        :return:
        """
        count_vacancy = 0
        HH.vacancy_page = 0
        while True:
            vacancies = HH.get_vacancies(url)
            for vacancy in vacancies['items']:
                exemplar = HH(vacancy['name'],
                              vacancy['area']['name'],
                              vacancy['salary'],
                              vacancy['alternate_url'],
                              vacancy['employer']['name'],
                              vacancy['snippet']['responsibility'],
                              vacancy['id'],
                              vacancy['employer']['id'],
                              vacancy['employer']['alternate_url']
                              )
                HH.lst_exemplars.append(exemplar)
                count_vacancy += 1

            if count_vacancy < vacancies['found']:
                HH.vacancy_page += 1
                pass
            else:
                return HH.lst_exemplars

    @classmethod
    def search_company(cls, name_company: str):
        """
        функция для поиска компании строго по заданному тексту, после добавляет в файл COMPANIES.json в нужном формате
        :param name_company: компания для поиска, вводимая пользователем
        :return:
        """
        companies = requests.get(HH.url_employers, params={'text': name_company,
                                                           'sort_by': 'by_vacancies_open',
                                                           'per_page': 10}).json()
        if not companies['items']:
            return f'Такой компании нет на HH.ru'

        for company in companies['items']:
            if company['name'].lower() == name_company.lower():
                company_to_add = {
                    'Company_name': company['name'],
                    'Company_id': company['id'],
                    'Open_vacancies': company['open_vacancies'],
                    'vacancies_url': company['vacancies_url']
                }
                return company_to_add


class JSONSaver:

    @classmethod
    def load_file(cls, file='Companies.json'):
        """
        Открывает json-файл с компаниями
        :param file: json-файл
        :return: список словарей компаний
        """
        with open(file, 'r', encoding='utf-8') as file:
            companies = json.load(file)
        return companies

    @classmethod
    def add_company(cls, text: list):
        """
        Записывает в конец файла компании
        :param text: вакансии
        """
        companies = JSONSaver.load_file()
        with open('Companies.json', 'w', encoding='utf-8') as file:
            companies.append(text)
            json.dump(companies, file, indent=2, ensure_ascii=False)

    @classmethod
    def clear_file(cls):
        """
        Метод полной очистки файла
        :return: Чистый файл
        """
        with open('Companies.json', 'w', encoding='utf-8') as file:
            file.write('[]')

    @classmethod
    def remove_company(cls, company):
        companies = JSONSaver.load_file()
        with open('Companies.json', 'w', encoding='utf-8') as file:
            companies.remove(company)
            json.dump(companies, file, indent=2, ensure_ascii=False)


class DBManager(StandartData, MixinFuncs):
    user = 'postgres'
    password = '57365'

    @classmethod
    def delete_tables(cls):
        """
        функция для очистки  sql таблиц
        :return:
        """
        sql_delete_tables = """
        TRUNCATE TABLE vacancy_full_data CASCADE;
        TRUNCATE TABLE id_vacancy_data CASCADE;
        TRUNCATE TABLE id_company_data CASCADE;
        """

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_delete_tables)
        connection.close()

    @classmethod
    def create_tables(cls):
        """
        функция создания таблиц и зависимостей в базе данных
        :return:
        """
        try:
            sql_create_tables = """CREATE TABLE id_vacancy_data
                     (
                         id_vacancy int NOT NULL,
                         name_vacancy varchar(120) NOT NULL,
                         url_vacancy varchar(100) NOT NULL
                     );
                     CREATE TABLE id_company_data
                     (
                         id_company int NOT NULL,
                         name_company varchar(80) NOT NULL,
                         url_company varchar(80) NOT NULL
                     );
                     CREATE TABLE vacancy_full_data
                     (
                         id_vacancy int NOT NULL,
                         id_company int NOT NULL,
                         salary int,
                         description varchar(500),
                         town varchar(55)
                     );
            
                     ALTER TABLE ONLY id_vacancy_data
                         ADD CONSTRAINT pk_id_vacancy PRIMARY KEY (id_vacancy);
            
                     ALTER TABLE ONLY  id_company_data
                         ADD CONSTRAINT pk_id_company PRIMARY KEY (id_company);
            
                     ALTER TABLE ONLY vacancy_full_data
                         ADD CONSTRAINT fk_id_vacancy FOREIGN KEY (id_vacancy) REFERENCES id_vacancy_data;
            
                     ALTER TABLE ONLY vacancy_full_data
                         ADD CONSTRAINT fk_id_company FOREIGN KEY (id_company) REFERENCES id_company_data;"""

            connection = DBManager.connect()
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            cursor.execute(sql_create_tables)
            connection.close()
        except psycopg2.errors.DuplicateTable:
            pass

    @classmethod
    def connect(cls):
        """
        функция настройки подключения к базе данных
        :return:
        """
        conn = psycopg2.connect(
            host='localhost',
            database='vacanciesbase',
            user=DBManager.user,
            password=DBManager.password)
        return conn

    @classmethod
    def create_database(cls):
        """
        Функция создания базы данных vacanciesbase
        :return:
        """
        try:
            connection = psycopg2.connect(
                host='localhost',
                user=DBManager.user,
                password=DBManager.password)

            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            sql_create_database = 'create database vacanciesbase'
            cursor.execute(sql_create_database)
            connection.close()
        except psycopg2.errors.DuplicateDatabase:
            pass

    @classmethod
    def load_vacancies_to_database(cls):
        """
        Функция добавления вакансий по всем работадателям из файла COMPANIES.json в базу данных vacanciesbase
        :return:
        """
        companies = JSONSaver.load_file()
        for company in companies:
            HH.add_vacancies_exemplars(company['vacancies_url'])

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        for company in companies:
            try:
                cursor.execute('INSERT INTO id_company_data values(%s, %s, %s)', (
                    company['Company_id'],
                    company['Company_name'],
                    company['vacancies_url']
                ))
            except psycopg2.errors.UniqueViolation:
                pass
        for vacancy_exemplar in HH.lst_exemplars:
            try:
                cursor.execute('INSERT INTO id_vacancy_data values(%s, %s, %s)', (
                    vacancy_exemplar.id_vacancy,
                    vacancy_exemplar.name,
                    vacancy_exemplar.url_vacancy
                ))
                cursor.execute('INSERT INTO vacancy_full_data values(%s, %s, %s, %s, %s)', (
                    vacancy_exemplar.id_vacancy,
                    vacancy_exemplar.id_company,
                    vacancy_exemplar.salary,
                    vacancy_exemplar.snippet,
                    vacancy_exemplar.town
                ))
            except psycopg2.errors.UniqueViolation:
                pass
        connection.close()

    @classmethod
    def get_companies_and_vacancies_count(cls):
        """
        получает список всех компаний и количество вакансий у каждой компании
        :return:
        """
        sql_get = """
        SELECT name_company, count(*) as total_vac
        FROM vacancy_full_data
        INNER JOIN id_company_data USING(id_company)
        GROUP BY name_company
        """

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_get)
        rows = cursor.fetchall()
        connection.close()

        print('#' * 40, 'new_sql_request', '#' * 40, '\n')
        for row in rows:
            print(row)

    @classmethod
    def get_all_vacancies(cls):
        """
        получает список всех вакансий с
        указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию
        :return:
        """
        sql_get = """
        SELECT name_company, name_vacancy, salary, url_vacancy 
        FROM vacancy_full_data 
        INNER JOIN id_vacancy_data USING(id_vacancy) 
        INNER JOIN id_company_data USING(id_company)
        """

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_get)
        rows = cursor.fetchall()
        connection.close()

        print('#' * 40, 'new_sql_request', '#' * 40, '\n')
        for row in rows:
            print(row)

    @classmethod
    def get_avg_salary(cls):
        """
        получает среднюю зарплату по вакансиям
        :return:
        """
        sql_get = """
        SELECT FLOOR(AVG(salary)) AS average FROM vacancy_full_data 
        WHERE salary IS NOT NULL 
        """

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_get)
        rows = cursor.fetchall()
        connection.close()

        print('#' * 40, 'new_sql_request', '#' * 40, '\n')
        for row in rows:
            print("Средняя зарплата по всем вакансиям - ", int(row[0]), "рублей")

    @classmethod
    def get_vacancies_with_higher_salary(cls):
        """
        получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        :return:
        """
        sql_get = """
        SELECT name_vacancy, name_company, salary, town, description, url_vacancy
        FROM vacancy_full_data
        INNER JOIN id_vacancy_data USING(id_vacancy)
        INNER JOIN id_company_data USING(id_company)
        WHERE salary > (
        SELECT FLOOR(AVG(salary)) as average from vacancy_full_data
        WHERE salary IS NOT NULL )
        """

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_get)
        rows = cursor.fetchall()
        connection.close()

        print('#' * 40, 'new_sql_request', '#' * 40, '\n')
        for row in rows:
            print(row)

    @classmethod
    def get_vacancies_with_keyword(cls, text):
        """
        получает список всех вакансий, в названии которых содержатся переданные в метод слова
        :return:
        """
        sql_get = f"""
        SELECT name_vacancy, name_company, salary, town, description, url_vacancy 
        FROM vacancy_full_data
        INNER JOIN id_vacancy_data USING(id_vacancy)
        INNER JOIN id_company_data USING(id_company)
        WHERE name_vacancy LIKE '%{text}%'"""

        connection = DBManager.connect()
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_get)
        rows = cursor.fetchall()
        connection.close()

        print('#' * 40, 'new_sql_request', '#' * 40, '\n')
        for row in rows:
            print(row)
