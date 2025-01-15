from abc import ABC, abstractmethod

class RemoteServiceInterface(ABC):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @abstractmethod
    def bind(self):
        pass

    @abstractmethod
    def register_method(self, method_name, method):
        pass

    @abstractmethod
    def run(self):
        pass
