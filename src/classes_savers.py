from abc import ABC, abstractmethod
import json


class SaverABC(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def save(self, *args):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def clear(self):
        pass


class SaverJSON(SaverABC):

    def __init__(self, filename):
        self.filename = filename

    def save(self, list_data, mode='w'):  # 'a' or 'w'
        """
        Сохраняет вакансии в файл.
        Можно перезаписать или дополнить.

        :param list_data:
        :param mode:
        :return:
        """

        if mode == 'a':
            old_set = set(self.load())
            for vacancy in list_data:
                old_set.add(vacancy)
            new_list = list(old_set)
            list_data = new_list

            len_old = len(old_set)
        else:
            len_old = 0

        len_added = len(list_data) - len_old

        dict_data = [item.convert_to_dict() for item in list_data]

        with open(self.filename, 'w', encoding="UTF-8") as f:
            json.dump(dict_data, f, indent=2, ensure_ascii=False)

        print(self.how_much_saved(len_added))

    def load(self):
        """
        Загружает вакансии из файла
        :return:
        """
        try:
            with open(self.filename, encoding="UTF-8") as f:
                new_data = json.load(f)
        except FileNotFoundError:
            print("Файл не существует")
            return None
        except json.decoder.JSONDecodeError:
            print("Ошибка чтения файла")
            return None

        return new_data

    def clear(self):
        """
        Удаляет данные из файла
        :return:
        """
        with open(self.filename, 'w', encoding="UTF-8") as f:
            f.write('')

    @staticmethod
    def how_much_saved(n):

        n_100 = n % 100
        n_10 = n % 10

        if (11 <= n_100 <= 14) or (5 <= n_10 <= 9) or (n_10 == 0):
            text = "вакансий записаны"
        elif n_10 == 1:
            text = "вакансия записана"
        else:  # 2 <= n_10 <= 4
            text = "вакансии записаны"

        return f'{n} {text} в файл'


class SaverTXT(SaverABC):

    def __init__(self, filename):
        self.filename = filename

    def save(self, data, mode):
        d = [item._employer.id for item in data]
        text = '\n'.join(set(d))

        with open(self.filename, 'w', encoding="UTF-8") as f:
            f.write(text)

    def load(self):

        with open(self.filename, 'r', encoding="UTF-8") as f:
            result = f.read()

        if result:
            return result.split('\n')
        else:
            return []



    def clear(self):
        pass

