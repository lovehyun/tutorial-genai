import os
import anthropic
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

class ModelComparison:
    def __init__(self):
        self.client = client
        self.models = [
            "claude-3-7-sonnet-20250219",  # 최신 모델
            "claude-3-5-sonnet-20240620", 
            "claude-3-haiku-20240307"
        ]
        self.metrics = {
            "response_time": [],
            "response_length": [],
            "model_name": []
        }
    
    def compare_models(self, prompt, max_tokens=1000, temperature=0.7):
        """여러 모델의 성능 비교"""
        results = {}
        
        for model in self.models:
            print(f"{model} 테스트 중...")
            
            try:
                start_time = pd.Timestamp.now()
                response = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                end_time = pd.Timestamp.now()
                response_time = (end_time - start_time).total_seconds()
                
                results[model] = {
                    "response": response.content[0].text,
                    "response_length": len(response.content[0].text),
                    "response_time": response_time
                }
                
                # 메트릭 저장
                self.metrics["model_name"].append(model)
                self.metrics["response_time"].append(response_time)
                self.metrics["response_length"].append(len(response.content[0].text))
                
                print(f"  응답 시간: {response_time:.2f}초")
                print(f"  응답 길이: {len(response.content[0].text)} 문자")
                print()
                
            except Exception as e:
                print(f"  오류 발생: {e}")
                results[model] = {"error": str(e)}
        
        return results
    
    def generate_comparison_report(self, prompt="인공지능의 미래에 대해 500자 이내로 설명해주세요."):
        """모델 비교 보고서 생성"""
        results = self.compare_models(prompt)
        
        # 데이터프레임 생성
        df = pd.DataFrame(self.metrics)
        
        # 결과 시각화
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 응답 시간 그래프
        ax1.bar(df['model_name'], df['response_time'], color='skyblue')
        ax1.set_title('응답 시간 비교')
        ax1.set_ylabel('시간 (초)')
        ax1.set_xticklabels(df['model_name'], rotation=45)
        
        # 응답 길이 그래프
        ax2.bar(df['model_name'], df['response_length'], color='lightgreen')
        ax2.set_title('응답 길이 비교')
        ax2.set_ylabel('문자 수')
        ax2.set_xticklabels(df['model_name'], rotation=45)
        
        plt.tight_layout()
        plt.savefig('model_comparison.png')
        plt.close()
        
        print("비교 보고서가 생성되었습니다. 'model_comparison.png' 파일을 확인하세요.")
        return results, df

# 사용 예시
if __name__ == "__main__":
    comparison = ModelComparison()
    results, df = comparison.generate_comparison_report()
    
    # 상세 응답 내용 출력
    for model, data in results.items():
        if "response" in data:
            print(f"모델: {model}")
            print(f"응답 (처음 200자): {data['response'][:200]}...\n")
