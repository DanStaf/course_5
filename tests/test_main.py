from src.main import collect_user_parameters
from src.main import hh_ru_user_interface
from src.classes_savers import SaverJSON
from src.classes_vacancy import Vacancy
from src.classes_aux import UserParameters
from src.classes_API import HHAPI

import pytest
import mock

FILENAME_1 = "../data/response_result.json"
FILENAME_2 = "../data/test.json"

vacancy_for_test = Vacancy('test_name',
                           'requirement',
                           'responsibility',
                           {'salary': 'salary'},
                           {'experience': 'experience'},
                           {'employment': 'employment'},
                           'url',
                           "2024-03-11T09:08:55+0300",
                           {'employer': 'employer'},
                           {'address': 'address'}
                           )

vacancy_1 = Vacancy('test_name_1',
                    'requirement',
                    'responsibility',
                    {
                        "from": 700000,
                        "to": 1000000,
                        "currency": "RUR",
                        "gross": True
                    },
                    {
                        "id": "between3And6",
                        "name": "От 3 до 6 лет"
                    },
                    {'employment': 'employment'},
                    'url',
                    "2024-03-11T09:08:55+0300",
                    {'employer': 'employer'},
                    {'address': 'address'}
                    )

vacancy_2 = Vacancy('test_name_2',
                    'requirement',
                    'responsibility',
                    {
                        "from": None,
                        "to": 10000,
                        "currency": "USD",
                        "gross": False
                    },
                    {
                        "id": "between3And6",
                        "name": "От 3 до 6 лет"
                    },
                    {'employment': 'employment'},
                    'url',
                    "2024-03-11T09:08:55+0300",
                    {'employer': 'employer'},
                    {'address': 'address'}
                    )

vacancy_3 = Vacancy('test_name_3',
                    'requirement',
                    'responsibility',
                    {
                        "from": 6500,
                        "to": None,
                        "currency": "EUR",
                        "gross": False
                    },
                    {
                        "id": "between3And6",
                        "name": "От 3 до 6 лет"
                    },
                    {'employment': 'employment'},
                    'url',
                    "2024-03-11T09:08:55+0300",
                    {'employer': 'employer'},
                    {'address': 'address'}
                    )

vacancy_4 = Vacancy('test_name_4',
                    'requirement',
                    'responsibility',
                    {
                        "from": None,
                        "to": None,
                        "currency": None,
                        "gross": None
                    },
                    {
                        "id": "between3And6",
                        "name": "От 3 до 6 лет"
                    },
                    {'employment': 'employment'},
                    'url',
                    "2024-03-11T09:08:55+0300",
                    {'employer': 'employer'},
                    {'address': 'address'}
                    )


def test_collect_user_parameters():

    with (mock.patch('builtins.input', side_effect=['5', '6', '7', '8'])):
        result = collect_user_parameters()
        assert result.text == '5'
        assert result.per_page == 6
        assert result.experience == "moreThan6"
        assert result.salary == 8


def test_user_parameters():

    parameters1 = UserParameters(['5', '6', '7', '8'])
    assert parameters1.text == '5'
    assert parameters1.per_page == 6
    assert parameters1.experience == "moreThan6"
    assert parameters1.salary == 8

    with pytest.raises(ValueError):
        UserParameters(['', '6', '7', '8'])

    parameters2 = UserParameters(['5', '', '', ''])
    assert parameters2.text == '5'
    assert parameters2.per_page is None
    assert parameters2.experience is None  # not is_digit
    assert parameters2.salary is None

    parameters3 = UserParameters(['5', '', '-100', ''])
    assert parameters3.experience is None  # negative

    parameters4 = UserParameters(['5', '', 'dsdnksd', ''])
    assert parameters4.experience is None  # not is_digit


def test_hh_ru_user_interface():

    test_input_1 = ['1', 'python', '8', '', '100000', 'w', 'n']

    with mock.patch('builtins.input', side_effect=test_input_1):
        assert hh_ru_user_interface(FILENAME_1) == 1

    test_input_2 = ['2', 'Senior', '', '', '200000', 'n', 'n']

    with mock.patch('builtins.input', side_effect=test_input_2):
        assert hh_ru_user_interface(FILENAME_1) == 2


def test_savers():
    result = [vacancy_for_test]

    saver = SaverJSON(FILENAME_2)
    assert saver.save(result) is None

    data = saver.load()
    assert data[0]['name'] == 'test_name'
    assert data[0]['url'] == 'url'

    saver.clear()
    assert saver.load() is None

    saver.filename = "test2"
    assert saver.load() is None


def test_vacancy():

    assert vacancy_for_test.name == 'test_name'

    vacancy_dict = vacancy_for_test.convert_to_dict()
    assert vacancy_dict['name'] == 'test_name'

    new_list = Vacancy.init_from_json([vacancy_dict])
    assert new_list[0].name == 'test_name'

    # get_salary

    salary_1 = vacancy_1.get_salary()
    assert salary_1['value'] == 1000000
    assert salary_1['text'] == '1000000 RUR gross'
    assert salary_1['value_rur'] == 1000000

    salary_2 = vacancy_2.get_salary()
    assert salary_2['value'] == 10000
    assert salary_2['text'] == '10000 USD net'
    assert salary_2['value_rur'] == 10000 * 91.87

    salary_3 = vacancy_3.get_salary()
    assert salary_3['value'] == 6500
    assert salary_3['text'] == '6500 EUR net'
    assert salary_3['value_rur'] == 6500 * 99.97

    salary_4 = vacancy_4.get_salary()
    assert salary_4['value'] == 0
    assert salary_4['text'] == 'Зарплата не задана'
    assert salary_4['value_rur'] == 0

    assert repr(vacancy_4) == "Vacancy: test_name_4 / Зарплата не задана / 2024-03-11 09:08"

    # compare

    assert vacancy_1 > vacancy_2
    assert vacancy_3 < vacancy_1
    assert vacancy_3 != vacancy_2
    assert vacancy_1 == vacancy_1

    # filter

    list_v = [vacancy_1, vacancy_2, vacancy_3, vacancy_4]
    filtered_1 = Vacancy.filter_vacancies(list_v,
                                          UserParameters(['1', '', '', ''])
                                          )
    assert len(filtered_1) == 1

    filtered_2 = Vacancy.filter_vacancies(list_v,
                                          UserParameters(['test', '', '', '500'])
                                          )
    assert len(filtered_2) == 3

    filtered_3 = Vacancy.filter_vacancies(list_v,
                                          UserParameters(['test', '2', '', '500'])
                                          )
    assert len(filtered_3) == 2
    assert filtered_3[0] > filtered_3[1]  # test correct order

    filtered_4 = Vacancy.filter_vacancies(list_v,
                                          UserParameters(['test', '2', '0', '500'])
                                          )
    assert len(filtered_4) == 0


def test_api():

    hh_api_1 = HHAPI(UserParameters(['text', '', '', '']), True)
    assert hh_api_1.get_token_info() != "Токен отсутствует"
    #assert hh_api_1.get_token_info() == "Токен: APPLP..."

    hh_api_2 = HHAPI(UserParameters(['python', '4', '0', '']))
    assert hh_api_2.get_token_info() == "Токен отсутствует"

    # get vacancies

    result = hh_api_2.get_vacancies()
    assert len(result) <= 4

    for each_vacancy in result:
        assert each_vacancy.get_experience() == "noExperience"

