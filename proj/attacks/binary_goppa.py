from proj.attacks.random_linear_code import LinearCodeAttack


class BinaryGoppaCodeAttack(LinearCodeAttack):

    def __init__(self, linear_code):
        super().__init__(linear_code)

    def attack(self):
        pass
