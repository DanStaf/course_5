from src.classes_API import HHAPI
from src.classes_aux import UserParameters
from src.classes_savers import SaverJSON, SaverTXT
from src.classes_vacancy import Vacancy
from src.classes_DB import DBManager

FILENAME = "data/response_result.json"
FILE_EMP = "../data/employers.txt"

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


def hh_ru_get_all_vacancies_all_employers(filename=FILE_EMP):
    hh_api = HHAPI()
    result = hh_api.get_vacancies()

    new_saver = SaverTXT(filename)
    new_saver.save(result, 'w')

    return result


def hh_ru_get_vacancies(ten_employers):
    hh_api = HHAPI(ten_employers)
    return hh_api.get_vacancies()


def get_ten_employers_from_file(filename=FILE_EMP):
    new_saver = SaverTXT(filename)
    employers_list = new_saver.load()
    if len(employers_list) >= 10:
        return employers_list[:10]
    else:
        return employers_list


def print_vacancies(data):
    print("Вакансий: ", len(data))
    [print(item._employer.id, ':', item.name) for item in data]

    emp_set = set([item._employer.id for item in data])
    print("Работодателей: ", len(emp_set))
    print(emp_set)


def get_employers(vacancies):

    employers = [item._employer for item in vacancies]

    employers_set = []
    for new_employer in employers:

        id_set = [old_employer.id for old_employer in employers_set]
        if new_employer.id not in id_set:
            employers_set.append(new_employer)

    #[print(item) for item in employers_set]

    return employers_set  # list


def interface():

    print("Hello!")

    print("\nПолучаем все вакансии с сайта hh.ru:")
    all_vacancies = hh_ru_get_all_vacancies_all_employers()
    print_vacancies(all_vacancies)

    print("\nВыбираем 10 работодателей:")
    ten_employers = get_ten_employers_from_file()
    print(ten_employers)

    print("\nПолучаем вакансии с сайта hh.ru от 10 работодателей:")
    vacancies = hh_ru_get_vacancies(ten_employers)
    print_vacancies(vacancies)

    print("\nЗаписываем в БД:")
    db = DBManager()
    #db.drop_tables()
    db.create_tables()

    employers = get_employers(vacancies)

    employers_data = [item.prepare_for_db() for item in employers]
    employers_data_unique = db.check_lines_employers(employers_data)

    if employers_data_unique:
        print('Работодатели: ', [item[0] for item in employers_data_unique])
        db.fill_table('employers', employers_data_unique)

    vacancies_data = [item.prepare_for_db() for item in vacancies]
    vacancies_data_unique = db.check_lines_vacancies(vacancies_data)

    if vacancies_data_unique:
        print('Вакансии:')
        [print(item[11], ':' , item[0]) for item in vacancies_data_unique]
        columns = 'name, requirement, responsibility, salary_from, salary_to, salary_currency, salary_gross, experience, employment, url, published_at, employer_id, address'
        db.fill_table('vacancies', [item.prepare_for_db() for item in vacancies], columns)

    print("\nЗапросы из БД:")

    print("\nКоличество вакансий по компаниям:")
    vacancies_per_companies = db.get_companies_and_vacancies_count()
    [print(item) for item in vacancies_per_companies]

    print("\nСписок всех вакансий:")
    all_vacancies_from_db = db.get_all_vacancies()
    [print(item) for item in all_vacancies_from_db]

    print("\nСредняя зарплата от/до:")
    avg_salary = db.get_avg_salary()
    print(avg_salary)

    print("\nВакансии, у которых зарплата выше средней:")
    vacancies_with_higher_salary = db.get_vacancies_with_higher_salary()
    [print(item) for item in vacancies_with_higher_salary]

    print("\nВакансии, в названии которых содержатся переданные в метод слова:")
    vacancies_with_higher_salary = db.get_vacancies_with_keyword('Менеджер')
    [print(item) for item in vacancies_with_higher_salary]

    print("Bye!")

#########################

interface()

