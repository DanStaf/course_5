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

    # DDL, DML requests

    def _requests_with_commit(self, query):

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)

            conn.commit()

    def create_tables(self):

        e = self.check('employers')
        v = self.check('vacancies')
        c = self.check('currencies')
        if e and v and c:
            return "Tables exists"
        elif e or v or c:
            return "One of the tables exists"

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
                salary_from int,
                salary_to int,
                salary_currency varchar(3),
                salary_gross boolean,
                experience text,
                employment text,
                url text,
                published_at date,
                employer_id int REFERENCES employers(employer_id) NOT NULL,
                address text        
            );"""

        query_currencies = """
            CREATE TABLE currencies
            (
                currency varchar(3),
                rate float
                );

            INSERT INTO currencies (currency, rate)
            VALUES
            ('EUR', 100),
            ('USD', 90),
            ('RUR', 1)
            """
        self._requests_with_commit(query_vacancies +
                                   query_employers +
                                   query_currencies)

        return "Tables created"

    def drop_tables(self):

        query_drop = """DROP TABLE employers, vacancies, currencies"""

        self._requests_with_commit(query_drop)

        return "Tables dropped"

    def fill_table(self, table_name, data, columns=""):
        """
        data: matrix (list of lists)
        """

        data_len = len(data[0])
        insert_text = ("%s, "*data_len)[:-2]

        columns_for_insert_with_serial = f"({columns}) " if columns else ""

        query_fill_table = f"INSERT INTO {table_name}{columns_for_insert_with_serial} VALUES ({insert_text})"

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.executemany(query_fill_table, data)

            conn.commit()

    # SELECT requests

    def _requests_with_select(self, query):

        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query)

                rows = cur.fetchall()
                return rows

    def check(self, table_name):

        query_check = f"""SELECT EXISTS
            (
                SELECT * FROM INFORMATION_SCHEMA.TABLES
                WHERE table_catalog = 'hh'
                AND TABLE_NAME = '{table_name}') AS table_exists
            """

        rows = self._requests_with_select(query_check)
        return rows[0][0]

    def check_lines_employers(self, data):

        """
                так не сработало
                IF NOT EXISTS
                (SELECT employer_id FROM employers
                 WHERE employer_id in (229269)
                       INSERT INTO employers
                       VALUES (229269, 'text', 'text', True, True)
        """

        id_list = [item[0] for item in data]
        id_text = ", ".join(id_list)
        query_check_lines = f"SELECT employer_id FROM employers WHERE employer_id in ({id_text})"

        rows = self._requests_with_select(query_check_lines)

        return [item for item in data if item[0] not in [str(row[0]) for row in rows]]

    def check_lines_vacancies(self, data):
        url_list = ["'" + item[9] + "'" for item in data]  # url
        url_text = ", ".join(url_list)
        query_check_lines = f"SELECT url FROM vacancies WHERE url in ({url_text})"

        rows = self._requests_with_select(query_check_lines)

        return [item for item in data if item[9] not in [str(row[0]) for row in rows]]

    def get_companies_and_vacancies_count(self):
        """
        получает список всех компаний и количество вакансий у каждой компании.
        :return:
        """

        query = """
            SELECT employers.name, COUNT(vacancies.name)
FROM employers
INNER JOIN vacancies USING (employer_id)
GROUP BY employers.name
            """

        return self._requests_with_select(query)

    def get_all_vacancies(self, query_adder=""):
        """
        получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию.
        :return:
        """

        query = """
        SELECT employers.name, vacancies.name, salary_from, salary_to, url FROM vacancies
        INNER JOIN employers USING (employer_id)
        """ + query_adder

        return self._requests_with_select(query)

    def get_avg_salary(self):
        """
        получает среднюю зарплату по вакансиям.
        :return:
        """

        query = """
                SELECT avg(salary_from*rate) as ag_from, avg(salary_to*rate) as ag_to
                FROM vacancies
                INNER JOIN currencies
                ON (vacancies.salary_currency = currencies.currency)
                """

        result = self._requests_with_select(query)

        return result[0]

    def get_vacancies_with_higher_salary(self):
        """
        получает список всех вакансий, у которых
        зарплата выше средней по всем вакансиям.
        :return:
        """

        avg = self.get_avg_salary()

        query_adder = f"""
        WHERE vacancies.salary_from > {avg[0]}
        OR vacancies.salary_to > {avg[1]}
        """

        return self.get_all_vacancies(query_adder)

    def get_vacancies_with_keyword(self, text):
        """
        получает список всех вакансий, в названии
        которых содержатся переданные в метод слова,
        например python.
        :return:
        """

        query_adder = f"""
                WHERE vacancies.name LIKE '%{text}%'
                """

        return self.get_all_vacancies(query_adder)

#############
