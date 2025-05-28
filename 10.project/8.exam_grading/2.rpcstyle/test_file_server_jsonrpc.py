import asyncio
import json
import subprocess

async def test_jsonrpc_call(tool_name: str, arguments: dict):
    """JSON-RPC 형식으로 file_server.py 호출"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        process = subprocess.Popen(
            ["python", "file_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # JSON 요청 전달
        request_json = json.dumps(request)
        stdout, stderr = process.communicate(input=request_json, timeout=5)

        if stderr:
            print(f"❌ 오류: {stderr}")
        else:
            response = json.loads(stdout)
            print("✅ JSON-RPC 응답:")
            print(json.dumps(response, indent=2, ensure_ascii=False))

    except subprocess.TimeoutExpired:
        print("⏰ 타임아웃")
    except Exception as e:
        print(f"❌ 예외 발생: {e}")

# 테스트 실행
if __name__ == "__main__":
    asyncio.run(test_jsonrpc_call("list_answer_files", {"pattern": "*.txt"}))
