# log_generator.py
# pip install python-dotenv
import os, time, random, socket
from dotenv import load_dotenv
from datetime import datetime
import calendar

load_dotenv()
LOG_SAMPLE_PATH = os.getenv("LOG_SAMPLE_PATH", "./sample_auth.log")
HOSTNAME = os.getenv("LOG_HOSTNAME", socket.gethostname())

users = ["ubuntu", "root", "admin", "test", "guest"]
invalid_users = ["admin", "test", "oracle", "pi", "user"]
ips_ext = ["203.0.113.45", "203.0.113.88", "198.51.100.23", "198.51.100.33"]
ips_lan = ["192.168.0.12", "192.168.0.15", "10.0.0.7"]
procs = ["sshd", "CRON", "sudo"]

def ts_now():
    now = datetime.now()
    mon = calendar.month_abbr[now.month]  # Aug
    # Windows에서 %e가 안되니, 일(day)을 공백 패딩으로 수동 처리
    day = f"{now.day:2d}"
    return f"{mon} {day} {now.strftime('%H:%M:%S')}"

pid_counter = random.randint(1000, 3000)

def line_failed_password():
    ip = random.choice(ips_ext)
    user = random.choice(invalid_users)
    port = random.randint(40000, 60000)
    return f"{ts_now()} {HOSTNAME} sshd[{rand_pid()}]: Failed password for invalid user {user} from {ip} port {port} ssh2"

def line_accepted_password():
    ip = random.choice(ips_ext + ips_lan)
    user = random.choice(["ubuntu", "root"])
    port = random.randint(40000, 60000)
    return f"{ts_now()} {HOSTNAME} sshd[{rand_pid()}]: Accepted password for {user} from {ip} port {port} ssh2"

def line_session_open():
    user = random.choice(["ubuntu", "root"])
    return f"{ts_now()} {HOSTNAME} sshd[{rand_pid()}]: pam_unix(sshd:session): session opened for user {user} by (uid=0)"

def line_session_close():
    user = random.choice(["ubuntu", "root"])
    return f"{ts_now()} {HOSTNAME} sshd[{rand_pid()}]: pam_unix(sshd:session): session closed for user {user}"

def line_disconnect():
    ip = random.choice(ips_ext + ips_lan)
    port = random.randint(40000, 60000)
    who = random.choice(["user guest", "authenticating user root", "user ubuntu"])
    return f"{ts_now()} {HOSTNAME} sshd[{rand_pid()}]: Disconnected from {who} {ip} port {port}"

def line_cron_open():
    return f"{ts_now()} {HOSTNAME} CRON[{rand_pid()}]: pam_unix(cron:session): session opened for user root by (uid=0)"

def line_cron_close():
    return f"{ts_now()} {HOSTNAME} CRON[{rand_pid()}]: pam_unix(cron:session): session closed for user root"

def line_sudo_open():
    user = random.choice(["ubuntu"])
    return f"{ts_now()} {HOSTNAME} sudo:     {user} : TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND=/bin/apt update"

def line_sudo_session_open():
    user = random.choice(["ubuntu"])
    return f"{ts_now()} {HOSTNAME} sudo: pam_unix(sudo:session): session opened for user root by {user}(uid=0)"

def line_sudo_session_close():
    return f"{ts_now()} {HOSTNAME} sudo: pam_unix(sudo:session): session closed for user root"

def rand_pid():
    global pid_counter
    pid_counter += random.randint(1, 7)
    return pid_counter

TEMPLATES = [
    line_failed_password,
    line_failed_password,
    line_failed_password,
    line_accepted_password,
    line_session_open,
    line_session_close,
    line_disconnect,
    line_cron_open,
    line_cron_close,
    line_sudo_open,
    line_sudo_session_open,
    line_sudo_session_close,
]

def append_line(path, line):
    with open(path, "a", encoding="utf-8", errors="ignore") as f:
        f.write(line + "\n")

def ensure_file(path):
    if not os.path.exists(path):
        # 초기 몇 줄을 만들어서 시작.
        seed = [
            line_failed_password(),
            line_failed_password(),
            line_accepted_password(),
            line_session_open(),
            line_cron_open(),
            line_cron_close(),
        ]
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(seed) + "\n")

if __name__ == "__main__":
    print(f"[log_generator] appending every 5s to {LOG_SAMPLE_PATH} (Ctrl+C to stop)")
    ensure_file(LOG_SAMPLE_PATH)
    try:
        while True:
            line = random.choice(TEMPLATES)()
            append_line(LOG_SAMPLE_PATH, line)
            print(line)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[log_generator] stopped.")
