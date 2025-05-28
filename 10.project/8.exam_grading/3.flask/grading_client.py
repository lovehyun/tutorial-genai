#!/usr/bin/env python3
"""
MCP 채점 클라이언트 - 채점 로직을 담당
MCP 서버와 통신하여 파일을 읽고 결과를 저장
"""

import asyncio
import json
import os
import re
import subprocess
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class ExamGradingClient:
    def __init__(self):
        # OpenAI 클라이언트 초기화
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        self.exam_config = None
        self.results = []
    
    async def call_mcp_server(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """MCP 서버와 직접 통신 (명령행 방식)"""
        try:
            if arguments is None:
                arguments = {}
                
            # 명령행 인수 구성
            cmd = ["python", "file_server.py", tool_name]
            for key, value in arguments.items():
                cmd.extend([f"--{key}", str(value)])
            
            print(f"🔧 MCP 호출: {' '.join(cmd)}")
            
            # 서버 실행
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30초 타임아웃
                encoding='utf-8'
            )
            
            if process.stderr:
                print(f"⚠️  서버 경고: {process.stderr}")
            
            if process.stdout:
                try:
                    result = json.loads(process.stdout)
                    return result
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 파싱 실패: {e}")
                    print(f"원시 출력: {process.stdout[:200]}...")
                    return {"error": f"JSON 파싱 실패: {process.stdout[:200]}"}
            
            return {"error": "서버 응답이 없습니다"}
            
        except subprocess.TimeoutExpired:
            return {"error": "서버 응답 타임아웃"}
        except Exception as e:
            return {"error": f"MCP 통신 오류: {e}"}
    
    async def load_exam_config(self) -> bool:
        """시험 설정 로드"""
        print("📚 시험 설정 로드 중...")
        result = await self.call_mcp_server("read_exam_config")
        
        if "error" in result:
            print(f"❌ 설정 로드 실패: {result['error']}")
            return False
        
        if result.get("success"):
            self.exam_config = result["config"]
            print(f"✅ 시험 설정 로드 완료")
            print(f"   📋 시험명: {self.exam_config.get('exam_title', 'Unknown')}")
            print(f"   📊 총점: {self.exam_config.get('total_points', 100)}점")
            print(f"   📝 문제 수: {len(self.exam_config.get('questions', []))}개")
            return True
        else:
            print(f"❌ 설정 로드 실패: {result}")
            return False
    
    async def get_answer_files(self) -> List[Dict[str, Any]]:
        """답안 파일 목록 조회"""
        print("📁 답안 파일 목록 조회 중...")
        result = await self.call_mcp_server("list_answer_files", {"pattern": "*.txt"})
        
        if "error" in result:
            print(f"❌ 파일 목록 조회 실패: {result['error']}")
            return []
        
        if result.get("success"):
            files = result["files"]
            print(f"✅ {result['total_count']}개 답안 파일 발견")
            for file_info in files:
                print(f"   📄 {file_info['filename']} ({file_info['size']} bytes)")
            return files
        else:
            print(f"❌ 파일 목록 조회 실패: {result}")
            return []
    
    async def read_answer_file(self, filename: str) -> Dict[str, Any]:
        """특정 답안 파일 읽기"""
        result = await self.call_mcp_server("read_answer_file", {"filename": filename})
        
        if "error" in result:
            print(f"❌ 파일 읽기 실패 {filename}: {result['error']}")
            return {}
        
        if result.get("success"):
            return result
        else:
            print(f"❌ 파일 읽기 실패 {filename}: {result}")
            return {}
    
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

=== 출제 문제 ==={questions_text}

=== 채점 기준 ==={criteria_text}

=== 학생 답안 ===
{answer_content}

=== 채점 요청 ===
다음 JSON 형식으로만 응답해주세요. 다른 텍스트 없이 순수한 JSON만 반환:

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
    
    def clean_json_response(self, response_content: str) -> str:
        """OpenAI 응답에서 JSON 추출"""
        cleaned_content = response_content.strip()
        
        # 코드 블록 제거
        if cleaned_content.startswith('```json'):
            cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
        elif cleaned_content.startswith('```'):
            cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
        
        return cleaned_content.strip()
    
    def calculate_grade(self, total_score: int, total_points: int = 100) -> str:
        """점수에 따른 등급 계산"""
        if not self.exam_config:
            percentage = (total_score / total_points) * 100
        else:
            grade_scale = self.exam_config.get('grade_scale', {})
            if grade_scale:
                for grade, min_score in sorted(grade_scale.items(), key=lambda x: x[1], reverse=True):
                    if total_score >= min_score:
                        return grade
            percentage = (total_score / total_points) * 100
        
        # 기본 등급 체계
        if percentage >= 95: return "A+"
        elif percentage >= 90: return "A"
        elif percentage >= 85: return "B+"
        elif percentage >= 80: return "B"
        elif percentage >= 75: return "C+"
        elif percentage >= 70: return "C"
        elif percentage >= 65: return "D+"
        elif percentage >= 60: return "D"
        else: return "F"
    
    async def grade_single_answer(self, filename: str) -> Dict[str, Any]:
        """개별 답안 채점"""
        print(f"\n📝 채점 중: {filename}")
        
        # 파일 읽기
        file_data = await self.read_answer_file(filename)
        if not file_data or 'content' not in file_data:
            return {
                'filename': filename,
                'error': '파일 읽기 실패',
                'total_score': 0
            }
        
        print(f"   📄 파일 크기: {file_data.get('size', 0)} bytes")
        
        # 채점 프롬프트 생성
        prompt = self.build_grading_prompt(file_data['content'])
        
        try:
            print(f"   🤖 OpenAI API 호출 중...")
            
            # OpenAI API 호출
            response = await self.openai_client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.1'))
            )
            
            response_content = response.choices[0].message.content
            print(f"   ✅ API 응답 받음")
            
            # JSON 추출 및 파싱
            cleaned_content = self.clean_json_response(response_content)
            
            try:
                result = json.loads(cleaned_content)
                
                # 등급이 없으면 계산해서 추가
                if 'grade' not in result or not result['grade']:
                    total_points = self.exam_config.get('total_points', 100) if self.exam_config else 100
                    result['grade'] = self.calculate_grade(result.get('total_score', 0), total_points)
                
                print(f"   ✅ 채점 완료: {result.get('total_score', 0)}점 ({result.get('grade', 'N/A')})")
                
            except json.JSONDecodeError as json_err:
                print(f"   ⚠️  JSON 파싱 시도 중...")
                # 정규식으로 JSON 추출 시도
                json_match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        
                        # 등급 계산
                        if 'grade' not in result or not result['grade']:
                            total_points = self.exam_config.get('total_points', 100) if self.exam_config else 100
                            result['grade'] = self.calculate_grade(result.get('total_score', 0), total_points)
                        
                        print(f"   ✅ 채점 완료 (정규식): {result.get('total_score', 0)}점 ({result.get('grade', 'N/A')})")
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON 파싱 최종 실패")
                        result = {
                            "total_score": 0,
                            "overall_feedback": f"JSON 파싱 실패. 원시 응답: {cleaned_content[:200]}...",
                            "error": "JSON format error",
                            "grade": "F"
                        }
                else:
                    print(f"   ❌ JSON 구조를 찾을 수 없음")
                    result = {
                        "total_score": 0,
                        "overall_feedback": f"JSON 구조 없음. 응답: {cleaned_content[:200]}...",
                        "error": "No JSON structure found",
                        "grade": "F"
                    }
            
            result['filename'] = filename
            return result
            
        except Exception as e:
            print(f"   ❌ 채점 오류: {e}")
            return {
                'filename': filename,
                'error': str(e),
                'total_score': 0,
                'grade': 'F'
            }
    
    async def batch_grade_answers(self) -> List[Dict[str, Any]]:
        """모든 답안 일괄 채점"""
        print("🚀 일괄 채점 시작\n")
        
        # 설정 로드
        if not await self.load_exam_config():
            return []
        
        # 답안 파일 목록 조회
        answer_files = await self.get_answer_files()
        if not answer_files:
            return []
        
        print(f"\n📊 {len(answer_files)}개 답안 채점 시작...")
        print("=" * 50)
        
        # 순차적으로 채점
        results = []
        for i, file_info in enumerate(answer_files):
            print(f"\n📈 진행률: {i+1}/{len(answer_files)}")
            result = await self.grade_single_answer(file_info['filename'])
            results.append(result)
            
            # API 제한 방지
            if i < len(answer_files) - 1:
                print(f"   ⏱️  잠시 대기 중... (API 제한 방지)")
                await asyncio.sleep(2)
        
        self.results = results
        print("\n🎉 모든 답안 채점 완료!")
        return results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """채점 결과 요약 생성"""
        if not self.results:
            return {"error": "채점 결과가 없습니다."}
        
        valid_results = [r for r in self.results if 'total_score' in r and 'error' not in r]
        
        if not valid_results:
            return {"error": "유효한 채점 결과가 없습니다."}
        
        scores = [r['total_score'] for r in valid_results]
        total_points = self.exam_config.get('total_points', 100) if self.exam_config else 100
        
        # 등급별 분포
        grade_distribution = {}
        for result in valid_results:
            grade = result.get('grade', 'F')
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # 문제별 평균 점수
        question_averages = {}
        if valid_results and 'question_scores' in valid_results[0]:
            questions = valid_results[0]['question_scores']
            for q in questions:
                q_num = q.get('question_number', 0)
                scores_for_q = []
                for result in valid_results:
                    q_scores = result.get('question_scores', [])
                    for qs in q_scores:
                        if qs.get('question_number') == q_num:
                            scores_for_q.append(qs.get('score', 0))
                            break
                if scores_for_q:
                    question_averages[f"문제_{q_num}"] = round(sum(scores_for_q) / len(scores_for_q), 1)
        
        return {
            "시험_정보": {
                "시험명": self.exam_config.get('exam_title', '시험') if self.exam_config else '시험',
                "총점": total_points,
                "응시자_수": len(valid_results),
                "채점_완료_시간": asyncio.get_event_loop().time()
            },
            "점수_통계": {
                "평균_점수": round(sum(scores) / len(scores), 2),
                "최고_점수": max(scores),
                "최저_점수": min(scores),
                "표준편차": round((sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores))**0.5, 2),
                "중간값": sorted(scores)[len(scores)//2]
            },
            "등급_분포": grade_distribution,
            "점수_구간별_분포": {
                f"{int(total_points*0.9)}점_이상": len([s for s in scores if s >= total_points*0.9]),
                f"{int(total_points*0.8)}-{int(total_points*0.9-1)}점": len([s for s in scores if total_points*0.8 <= s < total_points*0.9]),
                f"{int(total_points*0.7)}-{int(total_points*0.8-1)}점": len([s for s in scores if total_points*0.7 <= s < total_points*0.8]),
                f"{int(total_points*0.6)}-{int(total_points*0.7-1)}점": len([s for s in scores if total_points*0.6 <= s < total_points*0.7]),
                f"{int(total_points*0.6)}점_미만": len([s for s in scores if s < total_points*0.6])
            },
            "문제별_평균점수": question_averages
        }
    
    async def save_results(self, filename: str = "grading_results.json") -> bool:
        """채점 결과 저장"""
        print(f"💾 채점 결과 저장 중... ({filename})")
        try:
            report_data = {
                "exam_config": self.exam_config,
                "summary": self.generate_summary_report(),
                "detailed_results": self.results,
                "grading_metadata": {
                    "grading_system": "MCP-based Exam Grading System",
                    "total_files_processed": len(self.results),
                    "successful_gradings": len([r for r in self.results if 'error' not in r]),
                    "failed_gradings": len([r for r in self.results if 'error' in r])
                }
            }
            
            result = await self.call_mcp_server("save_grading_result", {
                "results": report_data,
                "filename": filename
            })
            
            if "error" in result:
                print(f"❌ 결과 저장 실패: {result['error']}")
                return False
            
            if result.get("success"):
                print(f"✅ 채점 결과 저장 완료: {result.get('saved_to', filename)}")
                return True
            else:
                print(f"❌ 결과 저장 실패: {result}")
                return False
                    
        except Exception as e:
            print(f"❌ 결과 저장 오류: {e}")
            return False
    
    async def get_system_info(self):
        """시스템 정보 조회"""
        result = await self.call_mcp_server("get_system_info")
        if "error" not in result and result.get("success"):
            return result["system"]
        return {}
    
    def print_detailed_results(self, results: List[Dict[str, Any]], max_results: int = 5):
        """상세 결과 출력"""
        print("\n📋 === 개별 채점 결과 ===")
        
        valid_results = [r for r in results if 'error' not in r]
        error_results = [r for r in results if 'error' in r]
        
        # 점수순으로 정렬
        valid_results.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        print(f"\n🏆 상위 {min(max_results, len(valid_results))}개 결과:")
        for i, result in enumerate(valid_results[:max_results]):
            print(f"\n{i+1}. 📄 파일: {result['filename']}")
            print(f"   📊 총점: {result['total_score']}점")
            print(f"   🎯 등급: {result.get('grade', 'N/A')}")
            print(f"   💬 전체 피드백: {result.get('overall_feedback', 'N/A')[:100]}...")
            
            # 문제별 점수
            if 'question_scores' in result and result['question_scores']:
                print(f"   📝 문제별 점수:")
                for q in result['question_scores']:
                    q_num = q.get('question_number', '?')
                    score = q.get('score', 0)
                    max_score = q.get('max_score', 0)
                    print(f"      문제 {q_num}: {score}/{max_score}점")
            
            # 기준별 점수
            if 'criteria_scores' in result and result['criteria_scores']:
                print(f"   📏 기준별 점수:")
                for criteria, score in result['criteria_scores'].items():
                    print(f"      {criteria}: {score}점")
        
        # 오류 결과
        if error_results:
            print(f"\n⚠️  오류 발생 파일: {len(error_results)}개")
            for err in error_results:
                print(f"   ❌ {err.get('filename', 'Unknown')}: {err.get('error', 'Unknown error')}")
    
    async def run_grading(self):
        """전체 채점 프로세스 실행"""
        print("🎯 MCP 기반 시험 채점 시스템 시작")
        print("=" * 60)
        
        # 시스템 정보 출력
        system_info = await self.get_system_info()
        if system_info:
            print(f"🖥️  플랫폼: {system_info.get('platform', 'Unknown')}")
            print(f"📁 작업 디렉토리: {system_info.get('working_directory', 'Unknown')}")
            print(f"📂 답안 디렉토리: {system_info.get('exam_directory', 'Unknown')}")
        
        # 채점 실행
        results = await self.batch_grade_answers()
        
        if results:
            # 결과 요약 출력
            summary = self.generate_summary_report()
            print("\n📊 === 채점 결과 요약 ===")
            print("=" * 50)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            
            # 결과 저장
            await self.save_results()
            
            # 상세 결과 출력
            self.print_detailed_results(results)
            
            print("\n🎉 채점 시스템 실행 완료!")
            print("=" * 60)
            
        else:
            print("❌ 채점할 답안이 없거나 오류가 발생했습니다.")

async def main():
    """메인 함수"""
    try:
        client = ExamGradingClient()
        await client.run_grading()
    except ValueError as e:
        print(f"❌ 설정 오류: {e}")
        print("💡 .env 파일에 OPENAI_API_KEY를 설정해주세요.")
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())
