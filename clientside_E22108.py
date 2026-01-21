import socket
from struct import *
import random
import time

# Για έλεγχο λαθών, δηλαδή τι θα γινόταν αν ο client έδινε λάθος τιμές
# μπορόυν να αλλαχθούν τα άκρα x, y στις random.randint(x, y) συναρτήσεις

# Συνάρτηση για λήψη των πακέτων
def recv_all(sock, length):
    # Αρχικοποιηση κανού byte string για αποθήκευση δεδομένων
    data = b''
    while len(data) < length:
        # Διάβασμα δεδομένων
        more = sock.recv(length - len(data))
        # Error αν λάβουμε λάθος αριθμό δεδομένων 
        if not more:
            raise EOFError(f"Expected {length} bytes, got only {len(data)}.")
        # Τα νέα δεδομένα προσθέτονται στο συνολικό πακέτο
        data += more
    # Επιστρέφουμε όλα τα δεδομένα αφού έχουμε διαβάσει το πλήρες μήκος    
    return data

def send_multiplication(sock):
    n = random.randint(2, 10)
    numbers = [random.randint(-5, 5) for _ in range(n)]
    print("Πολλαπλασιασμός:", numbers)
    #Header του πακέτου
    header = pack('!BBxx', 1, n)
    #+--------------------+-----------------------------+----------------------------------+
    #|      Πράξη (1)     |     Πλήθος Αριθμών (N)      |            Padding(2bytes)       |   
    #+--------------------+-----------------------------+----------------------------------+

    body = pack('!' + 'h'*n, *numbers)
    #+--------------------+--------------------+--------------------+
    #|         h          |         h          |          h         | ...n times
    #+--------------------+--------------------+--------------------+

    sock.sendall(header + body)

    response = recv_all(sock, 8)
    code, count, result = unpack('!BBxxf', response)
    if code == 0:
        print("Αποτέλεσμα:", result)
    elif code==1:
        print("Μη αποδεκτό πλήθος αριθμών (N).")
    elif code==2:
        print("Έδωσες αριθμό μεγαλύτερο απο το επιτρεπτό όριο")
    elif code==3:
        print("Έδωσες αριθμό μικρότερο απο το επιτρεπτό όριο")
    elif code==4:
        print("Η σύνδεση έκλεισε πρώορα -> EOFError")
    elif code==5:
        print("Άγνωστο σφάλμα στα δεδομένα για πολλαπλασιασμό.")
    else:
        print("Άγνωστο σφάλμα στα δεδομένα για πολλαπλασιασμό.")

def send_average(sock):
    n = random.randint(2, 20)
    numbers = [random.randint(0, 200) for _ in range(n)]
    print("Μέσος όρος:", numbers)
    #Header του πακέτου
    header = pack('!BBxx', 2, n)
    #+--------------------+-----------------------------+----------------------------------+
    #|      Πράξη (2)     |     Πλήθος Αριθμών (N)      |            Padding(2bytes)       |   
    #+--------------------+-----------------------------+----------------------------------+

    body = pack('!' + 'H'*n, *numbers)
    #+--------------------+--------------------+--------------------+
    #|         H          |         H          |          H         | ...n times
    #+--------------------+--------------------+--------------------+

    sock.sendall(header + body)

    response = recv_all(sock, 8)
    code, count, result = unpack('!BBxxf', response)
    if code == 0:
        print("Αποτέλεσμα:", result)
    elif code==1:
        print("Μη αποδεκτό πλήθος αριθμών (N).")
    elif code==2:
        print("Έδωσες αριθμό μεγαλύτερο απο το επιτρεπτό όριο")
    elif code==3:
        print("Έδωσες αριθμό μικρότερο απο το επιτρεπτό όριο")
    elif code==4:
        print("Η σύνδεση έκλεισε πρώορα -> EOFError")
    elif code==5:
        print("Άγνωστο σφάλμα στα δεδομένα για εύρεση μέσου όρου.")
    else:
        print("Άγνωστο σφάλμα στα δεδομένα για εύρεση μέσου όρου.")

def send_subtraction(sock):
    n = random.randint(2, 10)
    set1 = [random.randint(0, 60000) for _ in range(n)]
    set2 = [random.randint(0, 60000) for _ in range(n)]
    print("Αφαίρεση:")
    print("  Σετ 1:", set1)
    print("  Σετ 2:", set2)
    #Header του πακέτου
    header = pack('!BBxx', 3, n)
    #+--------------------+-----------------------------+----------------------------------+
    #|      Πράξη (3)     |     Πλήθος Αριθμών (N)      |            Padding(2bytes)       |   
    #+--------------------+-----------------------------+----------------------------------+
    
    body = pack('!' + 'H'*(2*n), *(set1 + set2))
    #+--------------------+--------------------+--------------------+
    #|         H          |         H          |          H         | ...2*n times
    #+--------------------+--------------------+--------------------+
    sock.sendall(header + body)

    header_resp = recv_all(sock, 4)
    code, count = unpack('!BBxx', header_resp)

    if code == 0:
        body_resp = recv_all(sock, 4 * count)
        result = list(unpack('!' + 'i'*count, body_resp))
        print("Αποτέλεσμα:", result)
    elif code==1:
        print("Μη αποδεκτό πλήθος αριθμών (N).")
    elif code==2:
        print("Έδωσες αριθμό μεγαλύτερο απο το επιτρεπτό όριο")
    elif code==3:
        print("Έδωσες αριθμό μικρότερο απο το επιτρεπτό όριο")
    elif code==4:
        print("Η σύνδεση έκλεισε πρώορα -> EOFError")
    elif code==5:
        print("Άγνωστο σφάλμα στα δεδομένα για αφαίρεση.")
    else:
        print("Άγνωστο σφάλμα στα δεδομένα για αφαίρεση.")

# Σύνδεση με τον Server
serverIP = '127.0.0.1'
serverPort = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((serverIP, serverPort))

# Εκτέλεση όλων των πράξεων
send_multiplication(sock)
time.sleep(1)
send_average(sock)
time.sleep(1)
send_subtraction(sock)

sock.close()
