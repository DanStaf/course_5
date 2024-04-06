from abc import ABC, abstractmethod
import requests
import json
from src.classes_vacancy import Vacancy
from src.classes_aux import UserParameters


class AbcAPI(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class HHAPI(AbcAPI):
    """
    Класс для работы с API сайта hh.ru
    Параметры:
    text - текст запроса - обязательно
    token - опционально
    per_page - опционально
    experience - опционально
    salary - опционально
    """

    def __init__(self, user_parameters=None, is_token_needed=False, token_force_update=False):
        self.__token = self.__receive_token(is_token_needed, token_force_update)

        self.text = None
        self.per_page = 100
        self.experience = None
        self.salary = None


    @staticmethod
    def __receive_token(is_token_needed: bool, token_force_update: bool):
        """
        ДЛЯ ЗАПРОСА ВАКАНСИЙ ТОКЕН НЕ НУЖЕН!
        :return: None

        ДЛЯ ДОПОЛНИТЕЛЬНЫХ ЗАПРОСОВ МОЖНО ИСПОЛЬЗОВАТЬ ТОКЕН
        Запрос токена делается после подтверждения приложения на сайте hh.ru

        Данный access_token имеет неограниченный срок жизни.
        При повторном запросе ранее выданный токен отзывается и выдается новый.
        Запрашивать access_token можно не чаще, чем один раз в 5 минут
        :return: (token, software_name, software_email)
        """

        if not is_token_needed:
            return None

        # IF TOKEN IS NEEDED:

        with open('../data/API_token.json') as f:
            data = json.loads(f.read())

        if not ('HH_SOFTWARE_NAME' in data) or not ('HH_SOFTWARE_EMAIL' in data):
            print('Приложение не зарегистрировано на HH.RU. Продолжим без токена')
            return None

        elif ('HH_API_TOKEN' in data) and not token_force_update:
            # HH_API_TOKEN and HH_SOFTWARE_NAME and HH_SOFTWARE_EMAIL exist:
            return (data['HH_API_TOKEN'],
                    data['HH_SOFTWARE_NAME'],
                    data['HH_SOFTWARE_EMAIL'])

        elif ('HH_CLIENT_ID' not in data) or  ('HH_CLIENT_SECRET' not in data):
            # HH_API_TOKEN not exist or need to update
            # but HH_SOFTWARE_NAME and HH_SOFTWARE_EMAIL not exist

            print('Приложение не зарегистрировано на HH.RU. Продолжим без токена')
            return None

        else:
            # HH_API_TOKEN not exist or need to update
            # HH_SOFTWARE_NAME and HH_SOFTWARE_EMAIL exist

            client_id = data['HH_CLIENT_ID']
            client_secret = data['HH_CLIENT_SECRET']

            grant_type = 'client_credentials'
            parameters = f"grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}"
            url_post = "https://api.hh.ru/token"  # используемый адрес для отправки запроса

            response = requests.post(url_post, params=parameters)  # отправка POST-запроса

            if response.status_code == 200:
                token = response.json()['access_token']
                return (token,
                        data['HH_SOFTWARE_NAME'],
                        data['HH_SOFTWARE_EMAIL'])
            else:
                print('Токен не получен от HH.RU. Продолжим без токена')
                return None

    def get_token_info(self):

        if self.__token is None:
            return "Токен отсутствует"
        else:
            return f'Токен: {self.__token[0][:5]}...'

    def __get_headers(self):
        """
        Если токен есть, заполняем headers
        """

        if self.__token:
            token = self.__token[0]
            software_name = self.__token[1]
            software_email = self.__token[2]

            return {
                'Authorization': f'Bearer {token}',
                'HH-User-Agent': f'{software_name} ({software_email})'
            }
        else:
            return {}

    def get_vacancies(self):
        """
        Метод делает запрос вакансий с сайта hh.ru по указанным параметрам
        :return: список объектов класса Vacancy
        """

        headers = self.__get_headers()

        parameters = {'currency': 'RUR',
                      'order_by': 'salary_desc'
                      }

        if self.text:
            parameters['text'] = self.text
        if self.per_page:
            parameters['per_page'] = self.per_page
        if self.experience:
            parameters['experience'] = self.experience
        if self.salary:
            parameters['salary'] = self.salary


        url_get = 'https://api.hh.ru/vacancies'

        response = requests.get(url_get, params=parameters, headers=headers)

        if response.status_code == 200:
            vacancies = response.json()['items']

            return Vacancy.init_from_json(vacancies)

        else:
            result = response.json()['errors']
            print('Ошибка получения вакансий от HH.RU.', response.status_code, result)
            return None





"""
"vacancy_search_order": [
{
"id": "publication_time",
"name": "по дате"
},
{
"id": "salary_desc",
"name": "по убыванию дохода"
},
{
"id": "salary_asc",
"name": "по возрастанию дохода"
},
{
"id": "relevance",
"name": "по соответствию"
},
{
"id": "distance",
"name": "по удалённости"
}
],

"experience": [
{
"id": "noExperience",
"name": "Нет опыта"
},
{
"id": "between1And3",
"name": "От 1 года до 3 лет"
},
{
"id": "between3And6",
"name": "От 3 до 6 лет"
},
{
"id": "moreThan6",
"name": "Более 6 лет"
}
],
"""

######################
