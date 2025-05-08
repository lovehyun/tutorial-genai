import os
import anthropic
import json
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

class ModelParameterTester:
    def __init__(self, base_prompt="지구 온난화에 대해 설명해주세요."):
        self.client = client
        self.base_prompt = base_prompt
        self.model = "claude-3-7-sonnet-20250219"
        self.results = {}
    
    def test_temperature(self, temperatures=[0.0, 0.5, 1.0], iterations=2):
        """온도(temperature) 파라미터 테스트"""
        results = {}
        
        for temp in temperatures:
            temp_results = []
            print(f"온도(temperature) {temp} 테스트 중...")
            
            for i in range(iterations):
                start_time = time.time()
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=500,
                    temperature=temp,
                    messages=[{"role": "user", "content": self.base_prompt}]
                )
                elapsed_time = time.time() - start_time
                
                temp_results.append({
                    "iteration": i+1,
                    "response": response.content[0].text,
                    "response_length": len(response.content[0].text),
                    "response_time": elapsed_time
                })
            
            results[f"temp_{temp}"] = temp_results
        
        self.results["temperature_tests"] = results
        return results
    
    def test_max_tokens(self, max_tokens_list=[100, 500, 1000]):
        """max_tokens 파라미터 테스트"""
        results = {}
        
        for tokens in max_tokens_list:
            print(f"max_tokens {tokens} 테스트 중...")
            start_time = time.time()
            response = self.client.messages.create(
                model=self.model,
                max_tokens=tokens,
                temperature=0.5,
                messages=[{"role": "user", "content": self.base_prompt}]
            )
            elapsed_time = time.time() - start_time
            
            results[f"tokens_{tokens}"] = {
                "response": response.content[0].text,
                "response_length": len(response.content[0].text),
                "response_time": elapsed_time
            }
        
        self.results["max_tokens_tests"] = results
        return results
    
    def test_top_p(self, top_p_values=[0.5, 0.9, 1.0]):
        """top_p 파라미터 테스트"""
        results = {}
        
        for top_p in top_p_values:
            print(f"top_p {top_p} 테스트 중...")
            start_time = time.time()
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                top_p=top_p,
                messages=[{"role": "user", "content": self.base_prompt}]
            )
            elapsed_time = time.time() - start_time
            
            results[f"top_p_{top_p}"] = {
                "response": response.content[0].text,
                "response_length": len(response.content[0].text),
                "response_time": elapsed_time
            }
        
        self.results["top_p_tests"] = results
        return results
    
    def run_all_tests(self):
        """모든 파라미터 테스트 실행"""
        self.test_temperature()
        self.test_max_tokens()
        self.test_top_p()
        
        # 결과 저장
        with open("model_parameter_tests.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print("모든 테스트가 완료되었습니다. 'model_parameter_tests.json' 파일을 확인하세요.")
        return self.results

# 사용 예시
if __name__ == "__main__":
    tester = ModelParameterTester()
    tester.run_all_tests()
