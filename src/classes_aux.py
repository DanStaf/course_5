class UserParameters:

    def __init__(self, user_parameters):
        """
        user_parameters: [
        0 = text/name/description
        1 = N
        2 = experience
        3 = ~salary]
        """

        if user_parameters[0]:
            self.text = user_parameters[0]
        else:
            raise ValueError('Запрос некорректный')

        if user_parameters[1].isdigit():
            self.per_page = int(user_parameters[1])
        else:
            self.per_page = None

        if user_parameters[2].isdigit():
            int_experience = int(user_parameters[2])

            if int_experience < 0:
                self.experience = None
            elif int_experience == 0:
                self.experience = "noExperience"
            elif int_experience <= 3:
                self.experience = "between1And3"
            elif int_experience <= 6:
                self.experience = "between3And6"
            else:
                self.experience = "moreThan6"
        else:
            self.experience = None

        if user_parameters[3].isdigit():
            self.salary = int(user_parameters[3])
        else:
            self.salary = None

