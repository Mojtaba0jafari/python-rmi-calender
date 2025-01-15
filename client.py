from remoteServiceInterface import RemoteServiceInterface
import socket
import pickle
import re
import os
import datetime

#client stub
class ClientStub(RemoteServiceInterface):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self):
        pass

    def register_method(self, method_name, method):
        pass

    def run(self):
        pass

    def connect(self):
        #connecting to the server's port
        self.client.connect((self.host, self.port))

    def get_service_address(self):
        methods = 'calender'
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #connect to name server to get port and ip of server based on services
        client_socket.connect(('127.0.0.1', 55556))

        #send the method name to the send_service function
        client_socket.send(pickle.dumps(methods))

        #receive the IP address and port associated with the method
        data = client_socket.recv(4096)
        result = pickle.loads(data)
        print(f"IP and port for '{methods}': {result}")
        self.host = result[0]
        self.port = int(result[1])
        client_socket.close()


    def call_method(self, method_name, *args):
        method_info = {
            'name': method_name,
            'args': args
        }
        self.client.send(pickle.dumps(method_info))
        data = self.client.recv(4096)
        return pickle.loads(data)

#creat an object of client stub(RemoteClient)
client = ClientStub('127.0.0.1', 55557)
client.get_service_address()
client.connect()

#client
#event adder client side
class EventAdder:
    def __init__(self):
        self.req = []
        self.result = 'back'
    def manager(self):
        temp = input("enter your event type : ")
        #if client wants to cancel the operation
        if temp.lower() != 'back':
            self.req.append(temp)
        else:
            return self.result
        while True:
            temp = input("enter the date of your event (e.g: day/month(in number)/year): ")
            #checking if input is in the correct format or not
            pattern = re.compile(r'^\d+/\d+/\d+$')
            if temp.lower() == 'back':
                return self.result
            elif not re.match(pattern, temp):
                print("enter the date in correct format e.g day/month(in number)/year)")
                continue
            else:
                day, month, year = map(int, temp.split('/'))
                if not 1 <= day <= 30:
                    print('day must bet between 1 and 30 ')
                    continue
                elif not 1 <= month <= 12:
                    print('month must bet between 1 and 12 ')
                    continue
                elif not 1 <= year:
                    print('year must bet bigger than 0 ')
                    continue
                else:
                    self.req.append(temp)
                    break

        while True:
            temp = input("enter the time of your event (e.g: 23:59): ")
            #checking if input is in the correct format or not
            pattern = re.compile(r'^\d+:\d+$')
            if temp.lower() == 'back':
                return self.result
            elif not re.match(pattern, temp):
                print("enter the time in correct format e.g 23:59")
                continue
            else:
                hour, minute = map(int, temp.split(':'))
                if not 0<= hour <= 23:
                    print('hour must be between 0 to 23')
                    continue
                elif not 0 <= minute <= 59:
                    print('hour must be between 0 to 59')
                    continue
                else:
                    self.req.append(temp)
                    break

        while True:
            temp = input("How many minutes will your event last? : ")
            if temp.lower() == 'back':
                return self.result
            #checking if input is in the correct format or not
            elif not temp.isdigit() or int(temp) < 0:
                print("enter the time in correct format e.g 4")
                continue
            else:
                self.req.append(temp)
                break

        temp = input("write a description about your event (e.g: basketball): ")
        #if client wants to cancel the operation
        if temp.lower() != 'back':
            self.req.append(temp)
        else:
            return self.result

        temp = input("Where will your event take place? (e.g: tehran): ")
        #if client wants to cancel the operation
        if temp.lower() != 'back':
            self.req.append(temp)
        else:
            return self.result
        temp = ''
        self.req.append(temp)
        while True:
            temp = input("choose a name for your event (must be unique): ")
            #if client wants to cancel the operation
            if temp.lower() != 'back':
                self.req[-1] = temp
                self.result = client.call_method('add', self.req)
                if self.result == 'failed':
                    #get the current date and time for suggesting name
                    current_datetime = datetime.datetime.now()
                    print(temp,' already in use, suggestion: ', temp, current_datetime.date())
                    continue
                else:
                    return self.result
            else:
                return self.result

#event remover client side
class EventRemover:
    def __init__(self):
        self.result = 'back'
        self.indices = []
    def manager(self):
        while True:
            temp = input("Enter your key word for event that you want to delete e.g for name sport_basketball_12-04-1401"
                         " \tfor type basketball \nfor date 13/08/1399 \tfor location tehran : ")
            if temp == 'back':
                return self.result
            if temp != '':
                self.result, self.indices = client.call_method('search', temp)
                break
            else:
                print("invalid input")
                continue
        print('the Results: \nType of event, Date of event, Time of event, length of event, description about event, Location of event, Name of event')
        for i in range(len(self.result)):
            print(i+1, '. ', self.result[i])
        while True:
            temp = input("enter the number of the row you want to delete : ")
            if temp == 'back':
                self.result = 'back'
                return self.result
            elif int(temp) >= 1 and int(temp) <= len(self.result):
                self.result = client.call_method('remove', self.indices[int(temp)-1])
                return self.result
            else:
                print("invalid input")

#event searcher client side
class searcher:
    def __init__(self):
        self.result = 'back'
    def manager(self):
        while True:
            temp = input("Enter your key word e.g for name sport_basketball_12-04-1401 \tfor type basketball \nfor date 13/08/1399 \tfor location tehran: ")
            if temp == 'back':
                return self.result
            if temp != '':
                self.result, _ = client.call_method('search', temp)
                return self.result
            else:
                print("invalid input")

#event summary client side
class summary:
    def __init__(self):
        self.result = 'back'

    def manager(self):
        while True:
            temp = input("for getting summary of events based on year enter 1 for month enter 2 : ")
            if temp == 'back':
                return self.result

            elif int(temp) == 1:
                while True:
                    temp_1 = input("enter which year you want to get summary : ")
                    if temp_1 == 'back':
                        return self.result
                    elif temp_1.isdigit() and int(temp_1) >= 1:
                        self.result = client.call_method('summary', int(temp_1), int(temp))
                        return self.result
                    else:
                        print('invalid input')

            elif int(temp) == 2:
                while True:
                    temp_1 = input("enter which month you want to get summary (in number): ")
                    if temp_1 == 'back':
                        return self.result
                    elif temp_1.isdigit() and 1 <= int(temp_1) <= 12:
                        self.result = client.call_method('summary', int(temp_1), int(temp))
                        return self.result
                    else:
                        print('invalid input')

            elif int(temp) != 1 and int(temp) != 2:
                print("invalid input")
                continue

while True:
    # Clearing the Screen
    os.system('cls')
    action = input('**Event Manager**\nWhat action do you want to do?\n'
                   '1. add event\t2. remove event\n3. search\t4. view a summary\nenter your action: ')
    action = action.lower()
    # Clearing the Screen
    os.system('cls')

    #adding event to calender
    if action == 'add' or action == 'add event' or action == 'addevent' or action == '1':
        print("you are in adding event menu for cancelling operation enter 'back'")
        result = EventAdder().manager()
        if result == 'back':
            continue
        else:
            print(result)
            continue

    elif action == 'remove' or action == 'remove event' or action == 'removeevent' or action == '2':
        print("you are in removing event menu for cancelling operation enter 'back'")
        result = EventRemover().manager()
        if result == 'back':
            continue
        else:
            print('this row deleted \n', result)
            continue

    elif action == 'search' or action == 'search event' or action == 'searchevent' or action == '3':
        print("you are in search event menu for cancelling operation enter 'back'")
        result = searcher().manager()
        if result == 'back':
            continue
        elif result == 'not Found':
            print(result)
            continue
        else:
            print('the Results: \nType of event, Date of event, Time of event, length of event, description about event, Location of event, Name of event')
            for i in range(len(result)):
                print(result[i])
            continue

    elif action == 'summary' or action == 'view a summary' or action == 'viewasummary' or action == '4':
        print("you are in summary menu for cancelling operation enter 'back'")
        result = summary().manager()
        if result == 'back':
            continue
        elif result == 'not Found':
            print(result)
            continue
        else:
            print('the Results: \nType of event, Date of event, Time of event, length of event, description about event, Location of event, Name of event')
            for i in range(len(result)):
                print(result[i])
            continue

    else:
        print('invalid input')
