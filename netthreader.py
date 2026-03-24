import socket
import threading
from queue import Queue
import subprocess

# ====== COLORS ======
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

# ====== BANNER ======
def banner():
    print(BLUE + r"""
 _   _      _  _____ _                        _           
| \ | | ___| ||_   _| |__  _ __ ___  __ _  __| | ___ _ __ 
|  \| |/ _ \ __|| | | '_ \| '__/ _ \/ _` |/ _` |/ _ \ '__|
| |\  |  __/ |_ | | | | | | | |  __/ (_| | (_| |  __/ |   
|_| \_|\___|\__||_| |_| |_|_|  \___|\__,_|\__,_|\___|_| 

         NetThreader - Multi Threader Port Scanner  
         Created By VKP
""" + RESET)

# ====== INPUT ======

target = input("Enter target IP or domain: ")

# Resolve domain
try:
    target_ip = socket.gethostbyname(target)
except socket.gaierror:
    print("Invalid target!")
    exit()

# ====== DEFAULT PORT RANGE ======
start_port = 1
end_port = 65535
total_ports = end_port - start_port + 1
banner()
print("\n")
print(f"\nScanning: {target_ip} (1-65535 Ports)\n")

# ====== GLOBALS ======
queue = Queue()
open_ports = []
scanned_count = 0
lock = threading.Lock()

# ====== SCAN FUNCTION ======
def scan_port(port):
    global scanned_count
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((target_ip, port))
      
        if result == 0:
            with lock:
                open_ports.append(port)
                print(GREEN + f"[+] Port {port} Open" + RESET)
        
        sock.close()
    except:
        pass

# ====== WORKER ======
def worker():
    while True:
        port = queue.get()
        if port is None:
            break
        scan_port(port)
        queue.task_done()

# ====== THREADS ======
thread_count = 200
threads = []

for _ in range(thread_count):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()
    threads.append(t)

# ====== FILL QUEUE ======
for port in range(start_port, end_port + 1):
    queue.put(port)

# ====== WAIT ======
queue.join()

# Stop workers
for _ in range(thread_count):
    queue.put(None)

for t in threads:
    t.join()

# ====== SAVE RESULTS ======
filename = "scan_results.txt"
with open(filename, "w") as f:
    f.write(f"Scan Results for {target_ip}\n")
    f.write("="*30 + "\n")
    for port in open_ports:
        f.write(f"Port {port} OPEN\n")

# ====== DONE ======
print("\n\nScan Complete...")
print(GREEN + f"Open ports: {open_ports}" + RESET)
print(f"Results saved to {filename}")

# ====== NMAP COMMAND ======
print("\n" + CYAN + "[+]Preparing Nmap scan..." + RESET)

if open_ports:
    ports_str = ",".join(map(str, open_ports))
    nmap_cmd = ["nmap", "-sV", "-sC", "-Pn", "-p", ports_str, target_ip]
else:
    nmap_cmd = ["nmap", "-sV", "-sC", "-Pn", target_ip]

print(YELLOW + "Command: " + " ".join(nmap_cmd) + RESET)

# ====== ASK USER ======
choice = input("\nRun Nmap scan now? (y/n): ").lower()

if choice == 'y':
    print(CYAN + "\n[+] Launching Nmap...\n" + RESET)

    try:
        process = subprocess.Popen(nmap_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Live output stream
        for line in process.stdout:
            print(line, end="")

        process.wait()

        print(GREEN + "\nNmap scan completed ⚡" + RESET)

    except FileNotFoundError:
        print(" Nmap is not installed or not in PATH.")
else:
    print("Exiting... 👋")
