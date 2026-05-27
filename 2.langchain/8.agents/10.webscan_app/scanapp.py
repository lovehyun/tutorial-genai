from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType

import socket
import ssl
import psutil
import requests
import datetime

load_dotenv()

# ======== 서버 상태 점검 함수들 ========

def check_ssh(host="127.0.0.1", port=22):
    """SSH 서비스 상태 점검"""
    return run_port_check(host, port, "SSH")

def check_http(host="127.0.0.1", port=80):
    """HTTP 서비스 상태 점검"""
    return run_port_check(host, port, "HTTP")

def check_https(host="example.com", port=443):
    """HTTPS 및 SSL 인증서 점검"""
    return check_ssl_cert(host, port)

def check_mysql(host="127.0.0.1", port=3306):
    """MySQL 데이터베이스 연결 상태 점검"""
    return run_port_check(host, port, "MySQL")

def check_postgresql(host="127.0.0.1", port=5432):
    """PostgreSQL 데이터베이스 연결 상태 점검"""
    return run_port_check(host, port, "PostgreSQL")

def check_redis(host="127.0.0.1", port=6379):
    """Redis 서비스 연결 상태 점검"""
    return run_port_check(host, port, "Redis")

def check_mongodb(host="127.0.0.1", port=27017):
    """MongoDB 데이터베이스 연결 상태 점검"""
    return run_port_check(host, port, "MongoDB")

def check_system_resources():
    """시스템 리소스 사용량 점검"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        result = f"""
[시스템 리소스 상태]
• CPU 사용률: {cpu_percent}%
• 메모리 사용률: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
• 디스크 사용률: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)
        """.strip()
        
        # 임계치 경고
        warnings = []
        if cpu_percent > 80:
            warnings.append("⚠️ CPU 사용률이 높습니다!")
        if memory.percent > 80:
            warnings.append("⚠️ 메모리 사용률이 높습니다!")
        if disk.percent > 80:
            warnings.append("⚠️ 디스크 사용률이 높습니다!")
        
        if warnings:
            result += "\n\n[경고]\n" + "\n".join(warnings)
            
        return result
    except Exception as e:
        return f"[FAIL] 시스템 리소스 점검 실패 → {str(e)}"

def check_running_processes():
    """실행 중인 주요 프로세스 점검"""
    try:
        important_processes = ['nginx', 'apache2', 'mysql', 'postgresql', 'redis', 'docker', 'ssh']
        running = []
        not_running = []
        
        all_processes = [p.name() for p in psutil.process_iter()]
        
        for process in important_processes:
            if any(process in p.lower() for p in all_processes):
                running.append(process)
            else:
                not_running.append(process)
        
        result = "[프로세스 상태]\n"
        if running:
            result += "✅ 실행 중: " + ", ".join(running) + "\n"
        if not_running:
            result += "❌ 중지됨: " + ", ".join(not_running)
            
        return result
    except Exception as e:
        return f"[FAIL] 프로세스 점검 실패 → {str(e)}"

def check_network_connectivity():
    """네트워크 연결성 점검"""
    try:
        test_hosts = [
            ('google.com', 80),
            ('8.8.8.8', 53),
            ('cloudflare.com', 80)
        ]
        
        results = []
        for host, port in test_hosts:
            try:
                sock = socket.create_connection((host, port), timeout=3)
                sock.close()
                results.append(f"✅ {host}:{port} 연결 성공")
            except:
                results.append(f"❌ {host}:{port} 연결 실패")
        
        return "[네트워크 연결성]\n" + "\n".join(results)
    except Exception as e:
        return f"[FAIL] 네트워크 점검 실패 → {str(e)}"

def check_disk_space():
    """디스크 공간 상세 점검"""
    try:
        partitions = psutil.disk_partitions()
        results = ["[디스크 공간 상태]"]
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                percent = usage.percent
                status = "⚠️" if percent > 80 else "✅"
                
                results.append(
                    f"{status} {partition.mountpoint}: {percent}% "
                    f"({usage.used // (1024**3)}GB / {usage.total // (1024**3)}GB)"
                )
            except:
                continue
                
        return "\n".join(results)
    except Exception as e:
        return f"[FAIL] 디스크 점검 실패 → {str(e)}"

def check_website_status(url=None):
    """웹사이트 상태 점검"""
    if not url:
        url = "http://localhost"
    
    try:
        response = requests.get(url, timeout=10)
        status_code = response.status_code
        response_time = response.elapsed.total_seconds()
        
        if status_code == 200:
            return f"✅ {url} 상태: HTTP {status_code} (응답시간: {response_time:.2f}초)"
        else:
            return f"⚠️ {url} 상태: HTTP {status_code} (응답시간: {response_time:.2f}초)"
            
    except requests.exceptions.Timeout:
        return f"❌ {url} 타임아웃"
    except requests.exceptions.ConnectionError:
        return f"❌ {url} 연결 실패"
    except Exception as e:
        return f"❌ {url} 점검 실패 → {str(e)}"

# ======== 공통 함수들 ========

def run_port_check(host, port, service_name="Service"):
    """포트 연결 상태 점검"""
    try:
        sock = socket.create_connection((host, port), timeout=3)
        sock.close()
        return f"✅ {service_name} ({host}:{port}) 연결 성공"
    except socket.timeout:
        return f"❌ {service_name} ({host}:{port}) 타임아웃"
    except ConnectionRefusedError:
        return f"❌ {service_name} ({host}:{port}) 연결 거부됨"
    except Exception as e:
        return f"❌ {service_name} ({host}:{port}) 연결 실패 → {str(e)}"

def check_ssl_cert(host, port):
    """SSL 인증서 상태 및 만료일 점검"""
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.connect((host, port))
            cert = s.getpeercert()
            
            # 만료일 파싱
            expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (expire_date - datetime.datetime.now()).days
            
            if days_left > 30:
                status = "✅"
            elif days_left > 7:
                status = "⚠️"
            else:
                status = "❌"
                
            return f"{status} {host} SSL 인증서 - 만료일: {cert['notAfter']} ({days_left}일 남음)"
            
    except Exception as e:
        return f"❌ SSL 인증서 점검 실패 ({host}) → {str(e)}"

def comprehensive_health_check():
    """전체 시스템 종합 점검"""
    checks = [
        ("시스템 리소스", check_system_resources()),
        ("실행 프로세스", check_running_processes()),
        ("네트워크 연결", check_network_connectivity()),
        ("디스크 공간", check_disk_space()),
        ("SSH 서비스", check_ssh()),
        ("HTTP 서비스", check_http()),
        ("MySQL 서비스", check_mysql()),
    ]
    
    result = "[🔍 종합 시스템 점검 결과]\n\n"
    for check_name, check_result in checks:
        result += f"=== {check_name} ===\n{check_result}\n\n"
    
    return result

# ======== LangChain Tools 등록 ========

# ======== Tool 래퍼 함수들 ========

def tool_check_ssh(query: str) -> str:
    """SSH 서비스 상태 점검 툴"""
    return check_ssh()

def tool_check_http(query: str) -> str:
    """HTTP 서비스 상태 점검 툴"""
    return check_http()

def tool_check_https(query: str) -> str:
    """HTTPS 및 SSL 인증서 점검 툴"""
    return check_https()

def tool_check_mysql(query: str) -> str:
    """MySQL 데이터베이스 상태 점검 툴"""
    return check_mysql()

def tool_check_postgresql(query: str) -> str:
    """PostgreSQL 데이터베이스 상태 점검 툴"""
    return check_postgresql()

def tool_check_redis(query: str) -> str:
    """Redis 서비스 상태 점검 툴"""
    return check_redis()

def tool_check_mongodb(query: str) -> str:
    """MongoDB 데이터베이스 상태 점검 툴"""
    return check_mongodb()

def tool_check_system_resources(query: str) -> str:
    """시스템 리소스 사용량 점검 툴"""
    return check_system_resources()

def tool_check_running_processes(query: str) -> str:
    """실행 중인 프로세스 점검 툴"""
    return check_running_processes()

def tool_check_network_connectivity(query: str) -> str:
    """네트워크 연결성 점검 툴"""
    return check_network_connectivity()

def tool_check_disk_space(query: str) -> str:
    """디스크 공간 점검 툴"""
    return check_disk_space()

def tool_check_website_status(query: str) -> str:
    """웹사이트 상태 점검 툴"""
    return check_website_status()

def tool_comprehensive_health_check(query: str) -> str:
    """종합 상태 점검 툴"""
    return comprehensive_health_check()

tools = [
    Tool(
        name="Check SSH",
        func=tool_check_ssh,
        description="SSH 서비스 (포트 22) 연결 상태를 점검합니다"
    ),
    Tool(
        name="Check HTTP",
        func=tool_check_http,
        description="HTTP 웹 서비스 (포트 80) 상태를 점검합니다"
    ),
    Tool(
        name="Check HTTPS SSL",
        func=tool_check_https,
        description="HTTPS 서비스와 SSL 인증서 상태를 점검합니다"
    ),
    Tool(
        name="Check MySQL",
        func=tool_check_mysql,
        description="MySQL 데이터베이스 (포트 3306) 연결 상태를 점검합니다"
    ),
    Tool(
        name="Check PostgreSQL",
        func=tool_check_postgresql,
        description="PostgreSQL 데이터베이스 (포트 5432) 연결 상태를 점검합니다"
    ),
    Tool(
        name="Check Redis",
        func=tool_check_redis,
        description="Redis 캐시 서버 (포트 6379) 연결 상태를 점검합니다"
    ),
    Tool(
        name="Check MongoDB",
        func=tool_check_mongodb,
        description="MongoDB 데이터베이스 (포트 27017) 연결 상태를 점검합니다"
    ),
    Tool(
        name="Check System Resources",
        func=tool_check_system_resources,
        description="CPU, 메모리, 디스크 사용률 등 시스템 리소스 상태를 점검합니다"
    ),
    Tool(
        name="Check Running Processes",
        func=tool_check_running_processes,
        description="주요 서비스 프로세스들의 실행 상태를 점검합니다"
    ),
    Tool(
        name="Check Network Connectivity",
        func=tool_check_network_connectivity,
        description="외부 네트워크 연결 상태를 점검합니다"
    ),
    Tool(
        name="Check Disk Space",
        func=tool_check_disk_space,
        description="모든 디스크 파티션의 용량 사용률을 상세히 점검합니다"
    ),
    Tool(
        name="Check Website Status",
        func=tool_check_website_status,
        description="웹사이트의 HTTP 응답 상태와 응답 시간을 점검합니다"
    ),
    Tool(
        name="Comprehensive Health Check",
        func=tool_comprehensive_health_check,
        description="모든 시스템 구성요소에 대한 종합적인 상태 점검을 수행합니다"
    ),
]

# ======== Agent 초기화 ========

def create_agent():
    """LangChain Agent 생성"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )
    
    return agent

def print_help():
    """도움말 출력"""
    help_text = """
🔧 서버 상태 점검 시스템

자연어로 서버 상태를 점검하실 수 있습니다!

예시 명령어:
• "SSH 서비스 상태 확인해줘"
• "데이터베이스 연결 상태는 어때?"
• "시스템 리소스 사용률 보여줘"
• "전체 서버 상태를 종합적으로 점검해줘"
• "웹사이트가 정상적으로 작동하나요?"
• "디스크 용량이 부족한지 확인해줘"
• "네트워크 연결에 문제가 있나요?"

명령어:
• help: 이 도움말 표시
• exit, quit: 프로그램 종료
"""
    print(help_text)

if __name__ == "__main__":
    print("서버 상태 점검 시스템을 시작합니다...")
    print("'help'를 입력하면 사용법을 확인할 수 있습니다.\n")
    
    agent = create_agent()
    
    while True:
        try:
            query = input("서버 점검 요청> ").strip()
            
            if not query:
                continue
                
            if query.lower() in ["exit", "quit", "종료"]:
                print("[INFO] 서버 점검 시스템을 종료합니다.")
                break
                
            if query.lower() in ["help", "도움말", "?"]:
                print_help()
                continue
            
            print("\n[INFO] 점검 중...")
            result = agent.run(query)
            print(f"\n[결과]:\n{result}\n")
            
        except KeyboardInterrupt:
            print("\n서버 점검 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {str(e)}\n")
