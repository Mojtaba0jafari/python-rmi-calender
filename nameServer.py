import socket
import pickle
import threading

class NameServer:
    def __init__(self):
        self.registered_methods = {}

    def get_service(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 55555))
        server_socket.listen(5)

        print("NameServer listening for servers to register their methods on port 55555\n")

        while True:
            conn, addr = server_socket.accept()
            print("Connected to", addr)

            data = conn.recv(4096)
            if not data:
                break

            arguments = pickle.loads(data)
            print("Received arguments:", arguments)

            self.registered_methods = arguments

            conn.close()

    def send_service(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 55556))
        server_socket.listen(5)

        print("NameServer listening for method queries on port 55556")

        while True:
            conn, addr = server_socket.accept()
            print("Connected to", addr)

            data = conn.recv(4096)
            if not data:
                break

            method_name_requested = pickle.loads(data)

            if method_name_requested in self.registered_methods['methods']:
                service_ip = self.registered_methods['ip']
                service_port = self.registered_methods['port']
                print('ip ', service_ip,'port ', service_port)
                conn.send(pickle.dumps((service_ip, service_port)))
            else:
                conn.send(pickle.dumps("Error: Method not found"))

            conn.close()

    def run_name_server(self):
        #create threads for get_service and send_service
        get_service_thread = threading.Thread(target=self.get_service)
        send_service_thread = threading.Thread(target=self.send_service)

        #start the threads
        get_service_thread.start()
        send_service_thread.start()

        #join the threads to the main thread
        get_service_thread.join()
        send_service_thread.join()



name_server = NameServer()
name_server.run_name_server()
