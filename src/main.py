from src.classes_API import HHAPI
from src.classes_aux import UserParameters
from src.classes_savers import SaverJSON, SaverTXT
from src.classes_vacancy import Vacancy

FILENAME = "data/response_result.json"


def collect_user_parameters():
    """
    Функция запрашивает данные от пользователя,
    возвращает объект UserParameters
    """
    vacancy_name = input('____\nВведите поисковый запрос для запроса вакансий: ')
    vacancy_amount = input('Введите количество вакансий для вывода в топ N: ')
    vacancy_keywords = input('Введите опыт работы (количество лет >= 0): ')
    vacancy_salary = input('Введите уровень зарплаты: ')

    return UserParameters([vacancy_name, vacancy_amount, vacancy_keywords, vacancy_salary])


def temp_parameters_for_API():
    """
    test
    """
    return UserParameters(['Python', '8', '', '100000'])


def temp_parameters_for_saver():
    """
    test
    """
    return UserParameters(['Senior', '', '', '200000'])


def hh_ru_user_interface(filename=FILENAME):
    """
    Основная логика программы:
    - предлагает два варианта работы, с сайта или из файла.
    - запрашивает параметры поиска.
    - выводит результат на экран.
    - предлагает записать в файл.
    - предлагает сделать новый запрос.
    """

    print('Программа для поиска и обработки вакансий')
    saver = SaverJSON(filename)

    while True:

        platform_no = int(input('____\nВыберите платформу: 1="hh", 2="Из файла JSON": '))

        if platform_no == 1:
            user_parameters = collect_user_parameters()
            #user_parameters = temp_parameters_for_API()

            hh_api = HHAPI(user_parameters)
            result = hh_api.get_vacancies()
            [print(item) for item in result]

            how_to_save = input('Добавить новые вакансии в файл (a), перезаписать файл (w) или пропустить (n)?')
            if how_to_save == 'a':
                saver.save(result, 'a')
            elif how_to_save == 'w':
                saver.save(result, 'w')
            else:
                pass

        elif platform_no == 2:
            user_parameters = collect_user_parameters()
            #user_parameters = temp_parameters_for_saver()

            vacancies = saver.load()

            if vacancies is not None:

                result = Vacancy.init_from_json(vacancies)
                filtered = Vacancy.filter_vacancies(result, user_parameters)

                [print(item) for item in filtered]

        else:
            print("Некорректный ввод")

        if input('Хотите запустить новый поиск? y/n: ') != 'y':
            break

    return platform_no

#hh_ru_user_interface()


def hh_ru_get_all_vacancies_all_employers():
    hh_api = HHAPI()
    result = hh_api.get_vacancies()
    [print(item._employer['id'], ':', item.name) for item in result]

    new_saver = SaverTXT("../data/employers.txt")
    new_saver.save(result, 'w')


def create_tables():

    pass


#########################

#hh_ru_get_all_vacancies_all_employers()
