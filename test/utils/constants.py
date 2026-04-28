"""테스트 프레임워크 상수 정의."""

from pathlib import Path

# 경로
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PYTHON = REPO_ROOT / ".venv" / "bin" / "python"

# 스캔 대상 디렉토리
SCAN_DIRS = [
    "1.openai",
    "2.langchain",
    "3.local",
    "4.anthropic",
    "7.google",
    "9.study",
    "10.project",
]

# 스캔 제외 패턴
SKIP_PATTERNS = ["__pycache__", ".venv", "node_modules", "test/"]

# API 키 패턴 (소스 코드에서 탐지)
API_KEY_PATTERNS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "TAVILY_API_KEY",
    "LANGCHAIN_API_KEY",
    "HUGGINGFACEHUB_API_TOKEN",
    "HF_TOKEN",
    "PINECONE_API_KEY",
    "SERPAPI_API_KEY",
    "COHERE_API_KEY",
    "os.getenv(",
    "os.environ[",
    "load_dotenv",
]

# 서버/서비스 실행 패턴
SERVICE_PATTERNS = [
    "app.run(",
    "uvicorn.run(",
    "gr.launch(",
    "gradio",
    "streamlit",
    "FastAPI()",
    "Flask(__name__)",
    "serve(",
    ".launch(",
]

# 사용자 입력 대기 패턴
INPUT_PATTERNS = [
    "input(",
    "sys.stdin",
    "readline()",
]

# 무거운 의존성 패턴 (로컬 모델 다운로드 등)
HEAVY_DEPS_PATTERNS = [
    "from_pretrained(",
    "AutoModel",
    "AutoTokenizer",
    "pipeline(",
    "torch.load(",
    "tensorflow",
    "SentenceTransformer(",
]
