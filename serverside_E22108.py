import socket
from struct import *
from _thread import *
import math

def recv_all(sock, length):
    # Αρχικοποιηση κανού byte string για αποθήκευση δεδομένων
    data = b''
    while len(data) < length:
        # Λήψη δεδομένων
        more = sock.recv(length - len(data))

        # Error αν λάβουμε λάθος αριθμό δεδομένων 
        if not more:
            raise EOFError(f"Expected {length} bytes, got only {len(data)}.")
        
        # Τα νέα δεδομένα προσθέτονται στο συνολικό πακέτο
        data += more
    # Επιστρέφουμε όλα τα δεδομένα αφού έχουμε διαβάσει το πλήρες μήκος    
    return data

# Code = 0  -> όλα πήγαν καλά
# Error code για λάθος πληθος αριθμών (N) -> 1
# Error code για αριθμό μεγαλύτερο απο το επιτρεπτό όριο = 2 
# Error code για αριθμό μικρότερο απο το επιτρεπτό όριο = 3 
# Error code για EOFError = 4
# Error code για Exception = 5

def handle_client(conn, addr):
    print("New client connected:", addr) # Ενημέρωση σύνδεσης με client 
    try:
        while True:
            # Πρώτα λαμβάνω μονο το header (4 bytes)
            header = conn.recv(4)         

            #+--------------------+-----------------------------+----------------------------------+
            #|       Πράξη        |     Πλήθος Αριθμών (N)      |            Padding(2bytes)       |   
            #+--------------------+-----------------------------+----------------------------------+      
                      
            # Έλεγχος αν υπήρχε λάθος απο μεριά client και το header είναι b'', δηλαδή False
            if not header: 
                break
            op_code, n = unpack('!BBxx', header)


            # Περιπτώσεις που έχουμε σωστό opperation code (op_code) αλλά μη δεκτό N (n)  
            # Στέλνω 8 bytes επειδή τόσα περιμένει να διαβάσει ο client
            if op_code == 1 and not (2 <= n <= 10):
                conn.sendall(pack('!BBxxf', 1, 0, 0.0))
                continue
            elif op_code == 2 and not (2 <= n <= 20):
                conn.sendall(pack('!BBxxf', 1, 0, 0.0))
                continue
            elif op_code == 3 and not (2 <= n <= 10):
                conn.sendall(pack('!BBxxf', 1, 0, 0.0))
                continue

            #0                    1                             2                                  4         8
            #+--------------------+-----------------------------+----------------------------------+---------+
            #|    Exit Code: 1    |    0 (Returns no result)    |            Padding(2bytes)       |  0.0(f) |                
            #+--------------------+-----------------------------+----------------------------------+---------+

            if op_code == 1:
                try:
                    #Λήψη 2*n bytes (Αφού κάθε αριθμός ειναι h = 2bytes και στέλνονται n αριθμοί απο τον client)
                    data = recv_all(conn, 2 * n)
                    nums = list(unpack('!' + 'h' * n, data)) # unpacking
                    
                    #Έλεγχος για μη αποδεκτή τιμή (exit code:2)
                    if any(x > 5 for x in nums):
                        conn.sendall(pack('!BBxxf', 2, 0, 0.0))
                        continue
                    elif any(x < -5 for x in nums):
                        conn.sendall(pack('!BBxxf', 3, 0, 0.0))
                        continue
                    
                    # Η συνάρτηση math.prod βρίσκει το γινόμενο όλων των αριθμών μαζί
                    result = math.prod(nums)
                    conn.sendall(pack('!BBxxf', 0, 1, result))  # Χρησιμοποιώ f για ευκολία (no padding)
                    #+--------------------+-----------------------------+----------------------------------+----------------------------------+
                    #|       0  (όλα καλά)|1 (επιστρέφεται 1 αποτέλεσμα)|            Padding(2bytes)       |         result (f)               |
                    #+--------------------+-----------------------------+----------------------------------+----------------------------------+
                except EOFError as e:
                    conn.sendall(pack('!BBxxf', 4, 0, 0.0))
                    break

                except Exception as e:
                    conn.sendall(pack('!BBxxf', 5, 0, 0.0))
                    continue

            elif op_code == 2:
                try:
                    data = recv_all(conn, 2 * n)
                    nums = list(unpack('!' + 'H' * n, data))

                    # Έλεγχος για μη απδεκτή τιμή  (Το x δεν μπορεί να είναι μικρότερο του 0 αφού είναι H (unsigned int) για αυτό δεν το ελέγχω)
                    if any(x > 200 for x in nums):
                        conn.sendall(pack('!BBxxf', 2, 0, 0.0))
                        continue

                    # Πράξη για εύρεση του μέσου όρου
                    avg = sum(nums) / n
                    conn.sendall(pack('!BBxxf', 0, 1, avg))   # Χρησιμοποιώ f για ευκολία (no padding)
                    #+--------------------+-----------------------------+----------------------------------+----------------------------------+
                    #|       0  (όλα καλά)|1 (επιστρέφεται 1 αποτέλεσμα)|            Padding(2bytes)       |         result  (f)              |
                    #+--------------------+-----------------------------+----------------------------------+----------------------------------+
                except EOFError as e:
                    conn.sendall(pack('!BBxx', 4, 0))
                    break

                except Exception as e:
                    conn.sendall(pack('!BBxx', 5, 0))
                    continue
            
            elif op_code == 3:
                try:
                    # Λήψη δεδομένων
                    data = recv_all(conn, 4 * n)
                    nums = list(unpack('!' + 'H' * (2 * n), data))
                    set1 = nums[:n]
                    set2 = nums[n:]

                    # print(f"Αφαίρεση | Σετ1: {set1} | Σετ2: {set2}")   -> Χρησιμοποιήθηκε για tests 

                    # Έλεγχος για μη απδεκτή τιμή  (Το x δεν μπορεί να είναι μικρότερο του 0 αφού είναι H (unsigned int) για αυτό δεν το ελέγχω)
                    if any(x > 60000 for x in nums):
                        conn.sendall(pack('!BBxxf', 2, 0, 0.0))
                        continue

                    # Υπολογισμός αποτελέσματος
                    result = [a - b for a, b in zip(set1, set2)]
                    #print(f"Αποτέλεσμα: {result}")   -> Χρησιμοποιήθηκε για tests

                    # Προετοιμασία και αποστολή απάντησης
                    msg = pack('!BBxx' + 'i' * n, 0, n, *result)
                    #+--------------------+--------------------------------+----------------------------------+------------+-----------+--
                    #|       0  (όλα καλά)|n (επιστρέφονται n αποτελέσματα)|            Padding(2bytes)       |     i      |      i    |   ...n times    
                    #+--------------------+--------------------------------+----------------------------------+------------+-----------+--
                    conn.sendall(msg)
                          
                except EOFError as e:
                    conn.sendall(pack('!BBxxf', 4, 0, 0.0))
                    break

                except Exception as e:
                    conn.sendall(pack('!BBxxf', 5, 0, 0.0))
                    continue
    except EOFError as e:
        conn.sendall(pack('!BBxxf', 4, 0, 0.0))
    except Exception as e:
        conn.sendall(pack('!BBxxf', 5, 0, 0.0))
    finally:
        print("Client disconnected:", addr)
        conn.close()

# Server Setup
serverIP = '127.0.0.1'
serverPort = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((serverIP, serverPort))
    s.listen()
    print("The server is ready to receive at port", serverPort)
    while True:
        conn, addr = s.accept()
        start_new_thread(handle_client, (conn, addr))
        #ThreadCount+=1
        #print('Thread Number: ' + str(ThreadCount))