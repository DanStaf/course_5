import psycopg2


class DBManager:
    """
    Класс DBManager должен использовать библиотеку psycopg2 для работы с БД.
    """

    def __init__(self):

        self.conn_params = {
            "host": "localhost",
            "database": "hh",
            "user": "postgres",
            "password": "admin"
        }

    def create_tables(self):

        query_vacancies = """CREATE TABLE employers
(
    employer_id int PRIMARY KEY,
    name varchar(100),
    vacancies_url text,
    accredited boolean,
    trusted boolean
);"""

        query_employers = """CREATE TABLE vacancies
(
    vacancy_id serial PRIMARY KEY,
    name varchar(100),
    requirement text,
    responsibility text,
    salary int,
    experience text,
    employment text,
    url text,
    published_at date,
    employer_id int,
    address text        
);"""

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query_vacancies)
                cur.execute(query_employers)

            conn.commit()

    def fill_table(self, table_name, data):
        """
        data: matrix (list of lists)
        """

        data_len = len(data[0])
        insert_text = ("%s, "*data_len)[:-2]

        query_fill_table = f"INSERT INTO {table_name} VALUES ({insert_text})"

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.executemany(query_fill_table, data)

            conn.commit()


    def get_companies_and_vacancies_count(self):
        """
        получает список всех компаний и количество вакансий у каждой компании.
        :return:
        """
        pass

    def get_all_vacancies(self):
        """
        получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        :return:
        """
        pass

    def get_avg_salary(self):
        """
        получает среднюю зарплату по вакансиям.
        :return:
        """

        pass

    def get_vacancies_with_higher_salary(self):
        """
        получает список всех вакансий, у которых
        зарплата выше средней по всем вакансиям.
        :return:
        """

        pass

    def get_vacancies_with_keyword(self):
        """
        получает список всех вакансий, в названии
        которых содержатся переданные в метод слова,
        например python.
        :return:
        """
        pass

