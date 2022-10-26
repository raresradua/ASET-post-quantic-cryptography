from abc import ABC, abstractmethod


# template method
class McEliece(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive
    operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """
    def __init__(self):
        """
        Constructor
        """
        self.encrypted_text = None
        self.decrypting_alg = None
        self.public_key = None
        self.private_key = None

    def operations(self, encrypted_text, public_key=None, private_key=None) -> None:
        """
        The template method defines the skeleton of an algorithm.
        """

        self.encrypted_text = encrypted_text
        self.decrypting_alg = encrypted_text.decrypting_alg
        if public_key is None or private_key is None:
            self.public_key, self.private_key = self.generate_keypair()
        else:
            self.public_key = public_key
            self.private_key = private_key

    @abstractmethod
    def generate_keypair(self) -> (..., ...):
        pass

    @abstractmethod
    def encrypt(self, message: str) -> ...:
        pass

    @abstractmethod
    def decrypt(self, cryptotext: str) -> ...:
        pass


class ConcreteClass(McEliece):
    """
    Concrete classes have to implement all abstract operations of the base
    class. They can also override some operations with a default implementation.
    """

    def generate_keypair(self) -> None:
        print("ConcreteClass says: Implemented First Operation")

    def encrypt(self, message) -> None:
        print("ConcreteClass says: Implemented Second Operation")

    def decrypt(self, cryptotext) -> None:
        print("ConcreteClass says: Implemented Third Operation")


# decorator
class Decorator(McEliece):
    """
    The base Decorator class follows the same interface as the other components.
    The primary purpose of this class is to define the wrapping interface for
    all concrete decorators. The default implementation of the wrapping code
    might include a field for storing a wrapped component and the means to
    initialize it.
    """

    _component: McEliece = None

    def __init__(self, component: McEliece) -> None:
        super().__init__()
        self._component = component

    @property
    def component(self) -> McEliece:
        """
        The Decorator delegates all work to the wrapped component.
        """

        return self._component

    def encrypt(self, message: str) -> ...:
        return self._component.encrypt()

    def decrypt(self, cryptotext: str) -> ...:
        return self._component.decrypt()


class ConcreteDecorator(Decorator):
    """
    Concrete Decorators call the wrapped object and alter its result in some
    way.
    """

    def encrypt2(self, message: str) -> ...:
        """
        Decorators may call parent implementation of the operation, instead of
        calling the wrapped object directly. This approach simplifies extension
        of decorator classes.
        """
        return "encrypt"

    def decrypt2(self, cryptotext: str) -> ...:
        return "decrypt"


def client_code(abstract_class: McEliece) -> None:
    """
    The client code calls the template method to execute the algorithm. Client
    code does not have to know the concrete class of an object it works with, as
    long as it works with objects through the interface of their base class.
    """

    # ...
    abstract_class.operations()  # template
    # ...
    # print("result decorator...") #decorator


if __name__ == "__main__":
    print("Result...")
    client_code(ConcreteClass())

    # test = ConcreteClass()
    # decorator = ConcreteDecorator(test)
    # client_code(decorator)
