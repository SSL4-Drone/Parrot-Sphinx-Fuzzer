import socket
from RandPayload import RandPayload

IP = "192.168.42.1"
PORT = 2233

def main():
    payload = RandPayload()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            for seq in range(255):
                data = payload.generate_random_payload(seq)
                sock.sendto(data, (IP, PORT))
                
                # Ulog, ack payload DB에 저장
                
    except Exception as ex:
        print("**[Error]** ", ex)
        sock.close()
        pass


if __name__ == "__main__":
    main()
