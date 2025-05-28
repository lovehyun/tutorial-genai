import os
import json
import yaml
import openai
from pathlib import Path
import asyncio
import aiofiles
from typing import List, Dict, Any
from dotenv import load_dotenv

# 필요한 패키지 설치:
# pip install openai aiofiles python-dotenv pyyaml

class ExamGradingSystem:
    def __init__(self):
        # 환경변수 로드
        load_dotenv()
        
        # 환경변수에서 설정 읽기
        self.directory_path = Path(os.getenv('EXAM_DIRECTORY'))
        self.client = openai.AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.results = []
        
        # 설정 파일 경로
        self.exam_config_path = Path(os.getenv('EXAM_CONFIG_PATH', 'exam_config.yaml'))
        self.exam_config = None
        
    async def load_exam_config(self) -> Dict[str, Any]:
        """시험 설정 파일(YAML) 로드"""
        try:
            async with aiofiles.open(self.exam_config_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.exam_config = yaml.safe_load(content)
                print(f"시험 설정 로드 완료: {self.exam_config_path}")
                return self.exam_config
        except FileNotFoundError:
            print(f"설정 파일을 찾을 수 없습니다: {self.exam_config_path}")
            return None
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}")
            return None
    
    async def read_answer_files(self) -> List[Dict[str, str]]:
        """디렉토리의 모든 txt 파일을 읽어오기"""
        if not self.directory_path.exists():
            print(f"답안 디렉토리가 존재하지 않습니다: {self.directory_path}")
            return []
            
        answer_files = []
        
        for file_path in self.directory_path.glob("*.txt"):
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    answer_files.append({
                        'filename': file_path.name,
                        'content': content,
                        'full_path': str(file_path)
                    })
                print(f"읽기 완료: {file_path.name}")
            except Exception as e:
                print(f"파일 읽기 오류 {file_path.name}: {e}")
                
        return answer_files
    
    def build_grading_prompt(self, answer_content: str) -> str:
        """채점 프롬프트 생성"""
        if not self.exam_config:
            return "설정 파일이 로드되지 않았습니다."
        
        # 문제 정보 추출
        questions = self.exam_config.get('questions', [])
        grading_criteria = self.exam_config.get('grading_criteria', {})
        
        # 문제 텍스트 구성
        questions_text = ""
        for i, question in enumerate(questions, 1):
            questions_text += f"\n문제 {i}: {question.get('question', '')}\n"
            if question.get('points'):
                questions_text += f"배점: {question['points']}점\n"
            if question.get('sample_answer'):
                questions_text += f"모범답안: {question['sample_answer']}\n"
        
        # 채점기준 텍스트 구성
        criteria_text = ""
        for category, details in grading_criteria.items():
            criteria_text += f"\n{category}: {details.get('points', 0)}점"
            if details.get('description'):
                criteria_text += f" - {details['description']}"
            if details.get('subcriteria'):
                for sub in details['subcriteria']:
                    criteria_text += f"\n  • {sub}"
        
        prompt = f"""
다음 시험의 학생 답안을 채점해주세요.

=== 시험 정보 ===
시험명: {self.exam_config.get('exam_title', '시험')}
총점: {self.exam_config.get('total_points', 100)}점
시험 시간: {self.exam_config.get('exam_duration', '미정')}

=== 출제 문제 ==={questions_text}

=== 채점 기준 ==={criteria_text}

=== 학생 답안 ===
{answer_content}

=== 채점 요청 ===
다음 JSON 형식으로만 응답해주세요. 다른 텍스트나 설명 없이 순수한 JSON만 반환해주세요:

{{
    "total_score": 총점(0-{self.exam_config.get('total_points', 100)}),
    "question_scores": [
        {{
            "question_number": 1,
            "score": 점수,
            "max_score": 만점,
            "feedback": "문제별 피드백"
        }}
    ],
    "criteria_scores": {{
        "정확성": 점수,
        "논리성": 점수,
        "명확성": 점수,
        "창의성": 점수,
        "표현력": 점수
    }},
    "overall_feedback": "전체적인 피드백",
    "strengths": ["잘한 점들"],
    "improvements": ["개선할 점들"],
    "grade": "등급(A+, A, B+, B, C+, C, D+, D, F)"
}}

중요: 반드시 유효한 JSON 형식으로만 응답하세요.
"""
        return prompt
    
    async def grade_single_answer(self, answer_data: Dict[str, str]) -> Dict[str, Any]:
        """개별 답안 채점"""
        print(f"채점 중: {answer_data['filename']}")
        prompt = self.build_grading_prompt(answer_data['content'])
        
        try:
            response = await self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
            )
            
            response_content = response.choices[0].message.content
            print(f"API 응답 받음: {answer_data['filename']}")
            
            # JSON 코드 블록 제거 (```json...``` 형태 처리)
            cleaned_content = response_content.strip()
            if cleaned_content.startswith('```json'):
                # ```json으로 시작하는 경우
                cleaned_content = cleaned_content[7:]  # '```json' 제거
                if cleaned_content.endswith('```'):
                    cleaned_content = cleaned_content[:-3]  # 마지막 '```' 제거
            elif cleaned_content.startswith('```'):
                # ```로만 시작하는 경우
                cleaned_content = cleaned_content[3:]
                if cleaned_content.endswith('```'):
                    cleaned_content = cleaned_content[:-3]
            
            cleaned_content = cleaned_content.strip()
            
            # JSON 파싱 시도
            try:
                result = json.loads(cleaned_content)
                print(f"JSON 파싱 성공: {answer_data['filename']}")
            except json.JSONDecodeError as json_err:
                print(f"JSON 파싱 오류 {answer_data['filename']}: {json_err}")
                print(f"정리된 내용 (처음 300자): {cleaned_content[:300]}...")
                
                # 더 강력한 JSON 추출 시도
                import re
                json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        print(f"정규식으로 JSON 추출 성공: {answer_data['filename']}")
                    except:
                        # 최종 실패시 기본 구조로 처리
                        result = {
                            "total_score": 0,
                            "overall_feedback": f"JSON 파싱 실패: {cleaned_content[:200]}...",
                            "error": "JSON format error"
                        }
                else:
                    result = {
                        "total_score": 0,
                        "overall_feedback": f"JSON 구조를 찾을 수 없음: {cleaned_content[:200]}...",
                        "error": "No JSON structure found"
                    }
            
            result['filename'] = answer_data['filename']
            result['grading_timestamp'] = asyncio.get_event_loop().time()
            print(f"채점 완료: {answer_data['filename']} - {result.get('total_score', 0)}점")
            return result
            
        except Exception as e:
            print(f"API 호출 오류 {answer_data['filename']}: {e}")
            return {
                'filename': answer_data['filename'],
                'error': str(e),
                'total_score': 0
            }
    
    async def batch_grade_answers(self) -> List[Dict[str, Any]]:
        """모든 답안 일괄 채점"""
        # 설정 파일 로드
        if not await self.load_exam_config():
            print("설정 파일 로드 실패. 채점을 중단합니다.")
            return []
        
        print("답안 파일들을 읽어오는 중...")
        answer_files = await self.read_answer_files()
        
        if not answer_files:
            print("읽을 답안 파일이 없습니다.")
            return []
        
        print(f"{len(answer_files)}개 답안 채점 시작...")
        
        # 안전한 순차 처리 (API 제한 방지)
        processed_results = []
        for i, answer_file in enumerate(answer_files):
            print(f"\n진행률: {i+1}/{len(answer_files)}")
            result = await self.grade_single_answer(answer_file)
            processed_results.append(result)
            
            # API 제한 방지를 위한 짧은 대기
            if i < len(answer_files) - 1:  # 마지막이 아니면 대기
                await asyncio.sleep(1)
        
        self.results = processed_results
        return processed_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """채점 결과 종합 리포트 생성"""
        if not self.results:
            return {"error": "채점 결과가 없습니다."}
        
        valid_results = [r for r in self.results if 'total_score' in r and 'error' not in r]
        
        if not valid_results:
            return {"error": "유효한 채점 결과가 없습니다."}
        
        scores = [r['total_score'] for r in valid_results]
        total_points = self.exam_config.get('total_points', 100) if self.exam_config else 100
        
        # 등급별 분포 계산
        grade_distribution = {}
        for result in valid_results:
            grade = result.get('grade', 'F')
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        summary = {
            "시험_정보": {
                "시험명": self.exam_config.get('exam_title', '시험') if self.exam_config else '시험',
                "총점": total_points,
                "응시자_수": len(valid_results)
            },
            "점수_통계": {
                "평균_점수": round(sum(scores) / len(scores), 2),
                "최고_점수": max(scores),
                "최저_점수": min(scores),
                "표준편차": round((sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores))**0.5, 2)
            },
            "등급_분포": grade_distribution,
            "점수_구간별_분포": {
                f"{int(total_points*0.9)}점_이상": len([s for s in scores if s >= total_points*0.9]),
                f"{int(total_points*0.8)}-{int(total_points*0.9-1)}점": len([s for s in scores if total_points*0.8 <= s < total_points*0.9]),
                f"{int(total_points*0.7)}-{int(total_points*0.8-1)}점": len([s for s in scores if total_points*0.7 <= s < total_points*0.8]),
                f"{int(total_points*0.6)}-{int(total_points*0.7-1)}점": len([s for s in scores if total_points*0.6 <= s < total_points*0.7]),
                f"{int(total_points*0.6)}점_미만": len([s for s in scores if s < total_points*0.6])
            }
        }
        
        return summary
    
    async def save_results(self, output_path: str = None):
        """채점 결과를 파일로 저장"""
        if output_path is None:
            output_path = self.directory_path / "grading_results.json"
        
        report_data = {
            "exam_config": self.exam_config,
            "summary": self.generate_summary_report(),
            "detailed_results": self.results,
            "grading_timestamp": str(asyncio.get_event_loop().time())
        }
        
        async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(report_data, ensure_ascii=False, indent=2))
        
        print(f"채점 결과 저장 완료: {output_path}")

# 사용 예시
async def main():
    # .env 파일에서 설정을 읽어오므로 여기서는 초기화만
    grading_system = ExamGradingSystem()
    
    # 모든 답안 채점
    results = await grading_system.batch_grade_answers()
    
    if results:
        # 결과 출력
        summary = grading_system.generate_summary_report()
        print("\n=== 채점 결과 요약 ===")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        
        # 결과 저장
        await grading_system.save_results()
        
        # 개별 결과 출력 (처음 3개만)
        print("\n=== 개별 채점 결과 (상위 3개) ===")
        for i, result in enumerate(results[:3]):
            if 'error' not in result:
                print(f"\n{i+1}. 파일: {result['filename']}")
                print(f"   총점: {result['total_score']}점")
                print(f"   등급: {result.get('grade', 'N/A')}")
                print(f"   전체 피드백: {result.get('overall_feedback', 'N/A')}")
                
                # 문제별 점수 출력
                if 'question_scores' in result:
                    print("   문제별 점수:")
                    for q in result['question_scores']:
                        print(f"     문제 {q.get('question_number', '?')}: {q.get('score', 0)}/{q.get('max_score', 0)}점")
            else:
                print(f"\n{i+1}. 파일: {result.get('filename', 'Unknown')}")
                print(f"   오류: {result['error']}")
                
        # 오류가 있는 파일들 요약
        error_files = [r for r in results if 'error' in r]
        if error_files:
            print(f"\n⚠️  오류 발생 파일: {len(error_files)}개")
            for err_file in error_files:
                print(f"   - {err_file.get('filename', 'Unknown')}: {err_file['error']}")
    else:
        print("채점할 답안이 없거나 오류가 발생했습니다.")

# 실행
if __name__ == "__main__":
    asyncio.run(main())
