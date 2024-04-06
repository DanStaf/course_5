from datetime import datetime
from src.classes_aux import UserParameters

CURRENCY_RATES = {
    'RUR': 1,
    'USD': 91.87,
    'EUR': 99.97
}

DT_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class Vacancy:

    def __init__(self, name: str, requirement: str, responsibility: str,
                 salary: dict, experience: dict, employment: dict,
                 url: str, published_at: str, employer: dict, address: dict):
        """
            "published_at": "2024-03-07T13:59:59+0300",
            "snippet": {
                "requirement": "",
                "responsibility": ""
            },
        """

        # валидация данных в классе UserParameters

        self.name = name
        self.requirement = requirement
        self.responsibility = responsibility

        self._salary = salary
        self._experience = experience
        self._employment = employment

        self._url = url
        self._published_at = datetime.strptime(published_at, DT_FORMAT)
        self._employer = employer
        self._address = address

    def __repr__(self):
        return f"Vacancy: {self.name} / {self.get_salary()['text']} / {self._published_at.strftime("%Y-%m-%d %H:%M")}"

    def get_salary(self):
        """
        salary - это словарь, в котором хранится зарплата от, до, валюта, гросс/нет
        Данный метод приводит зарплату к единой сумме и представлению
        Из диапазона выбирается максимальная зарплата.
        :return:
        """

        compare = []
        if self._salary['from'] is not None:
            compare.append(self._salary['from'])
        if self._salary['to'] is not None:
            compare.append(self._salary['to'])
        if compare:
            value = max(compare)
            text = (str(value) + ' ' + self._salary['currency'] + ' ' +
                    ('gross' if self._salary['gross'] else 'net')
                    )
            value_rur = value*CURRENCY_RATES[self._salary['currency']]
        else:
            value = 0
            value_rur = 0
            text = 'Зарплата не задана'

        return {'value': value, 'text': text, 'value_rur': value_rur}

    def convert_to_dict(self):
        """
        Метод для преобразования Вакансии в Словарь.
        Используется для записи в файл.
        :return:
        """

        return {
            'name': self.name,
            'snippet': {
                'requirement': self.requirement,
                'responsibility': self.responsibility
            },
            'salary': self._salary,
            'experience': self._experience,
            'employment': self._employment,
            'url': self._url,
            'published_at': self._published_at.strftime(DT_FORMAT),
            'employer': self._employer,
            'address': self._address
        }

    @classmethod
    def init_from_json(cls, vacancies_json):
        """
        Метод создаёт список Вакансий из JSON
        :param vacancies_json:
        :return:
        """

        return [Vacancy(item['name'],
                        item['snippet']['requirement'],
                        item['snippet']['responsibility'],
                        item['salary'],
                        item['experience'],
                        item['employment'],
                        item['url'],
                        item['published_at'],
                        item['employer'],
                        item['address']
                        ) for item in vacancies_json]

    @classmethod
    def filter_vacancies(cls, vacancies, user_parameters: UserParameters):
        """
        Метод фильтрует список Вакансий по заданным параметрам

        :param vacancies:
        :param user_parameters:
        :return:
        """

        filtered = []

        for vacancy in vacancies:

            lower_text = user_parameters.text.lower()
            if (
                    (lower_text in vacancy.name.lower()) or
                    (lower_text in vacancy.requirement.lower()) or
                    (lower_text in vacancy.responsibility.lower())
            ):
                if (
                        (user_parameters.salary is None) or
                        (user_parameters.salary <= vacancy.get_salary()['value_rur'])
                ):

                    if (
                            (user_parameters.experience is None) or
                            (user_parameters.experience == vacancy.get_experience())
                    ):
                        filtered.append(vacancy)

        filtered.sort(key=lambda s: s.get_salary()['value_rur'], reverse=True)

        return filtered[:user_parameters.per_page]

    def __gt__(self, other):
        a = self.get_salary()['value_rur']
        b = other.get_salary()['value_rur']

        return a > b

    def __lt__(self, other):
        a = self.get_salary()['value_rur']
        b = other.get_salary()['value_rur']

        return a < b

    def __eq__(self, other):
        a = self.get_salary()['value_rur']
        b = other.get_salary()['value_rur']

        return a == b

    def __ne__(self, other):
        a = self.get_salary()['value_rur']
        b = other.get_salary()['value_rur']

        return a != b

    def get_experience(self):
        return self._experience['id']

##################
