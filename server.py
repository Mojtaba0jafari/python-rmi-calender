from remoteServiceInterface import RemoteServiceInterface
import socket
import pickle
import threading

#server
class CalenderManager():
    def __init__(self):
        self.calender = [['speech', '2/10/1402', '23:00', '100m', 'ai', 'tehran', 'speech_ai_2-10-1402'],
                        ['sport', '12/04/1401', '12:01', '10m', 'basketball', 'qom', 'sport_basketball_12-04-1401'],
                        ['tutorial', '13/08/1399', '04:09', '21m', 'c++', 'tabriz', 'tutorial_c++_13-08-1399']]

    def event_searcher(self, request):
        results = [row for row in self.calender if request in row]
        indices = [index for index, row in enumerate(self.calender) if request in row]
        if not results:
            results = 'not Found'
            indices = -1
        return results, indices

    def name_checker(self, request):
        result, _ = self.event_searcher(request)
        if result == 'not Found':
            result = 'pass'
            return result
        else:
            result = 'failed'
            return result

    def event_adder(self, request):
        search_result = self.name_checker(request[-1])
        if search_result == 'pass':
            self.calender.append(request)
            results = 'your event with the name of ' + request[-1] + " added"
            return results
        else:
            return search_result

    def event_remover(self, request):
        deleted_row = self.calender.pop(request)
        return deleted_row

    def summary(self, request, flag):
        if flag == 1:
            pattern = f"/{request}"
            results = [row for row in self.calender if pattern in row[1]]
            if not results:
                results = 'not Found'
            return results
        else:
            print(type(request))
            pattern = f"/{request}/"
            results = [row for row in self.calender if pattern in row[1]]
            if not results:
                results = 'not Found'
            return results

#server stub
class ServerStub(RemoteServiceInterface):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.calender = CalenderManager()
        self.methods = {}
        self.registered_methods = {
            'methods': 'calender',
            'ip': self.host,
            'port': self.port
        }

    def bind(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print("Server listening on port", self.port)

    def register_method(self):
        self.methods['add'] = self.calender.event_adder
        self.methods['remove'] = self.calender.event_remover
        self.methods['search'] = self.calender.event_searcher
        self.methods['summary'] = self.calender.summary

        #notify name server of available methods, ip and port of server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #connecting to name server
        client_socket.connect(('127.0.0.1', 55555))
        #Serialize the data
        serialized_args = pickle.dumps(self.registered_methods)
        #send the data
        client_socket.send(serialized_args)
        #close the connection
        client_socket.close()

    def handle_client(self, conn):
        while True:
            data = conn.recv(4096)
            if not data:
                break

            method_info = pickle.loads(data)
            method_name = method_info['name']
            args = method_info['args']

            if method_name in self.methods:
                method = self.methods[method_name]
                result = method(*args)
                conn.send(pickle.dumps(result))
            else:
                conn.send(pickle.dumps(None))

        conn.close()

    def run(self):
        while True:
            conn, addr = self.server.accept()
            print("Connected to", addr)

            client_thread = threading.Thread(target=self.handle_client, args=(conn,))
            client_thread.start()

#initialize and run the server
event = ServerStub('127.0.0.1',55566)
event.register_method()
event.bind()
event.run()
