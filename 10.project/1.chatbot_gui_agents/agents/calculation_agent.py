import re
import math
import statistics
from typing import Dict, List, Any

class CalculationAgent:
    def __init__(self):
        """계산 Agent 초기화"""
        self.supported_operations = {
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/',
            'power': '**',
            'sqrt': 'sqrt',
            'log': 'log',
            'sin': 'sin',
            'cos': 'cos',
            'tan': 'tan'
        }
        
    def process(self, message: str) -> Dict[str, Any]:
        """메시지를 분석하고 계산 수행"""
        # 계산식 추출
        calculation = self._extract_calculation(message)
        
        if not calculation:
            return {
                'status': 'no_calculation',
                'message': '계산할 수식을 찾을 수 없습니다.',
                'result': None
            }
        
        try:
            # 계산 수행
            calc_result = self._perform_calculation(calculation)
            
            return {
                'status': 'success',
                'expression': calculation,
                'result': calc_result['result'],
                'steps': calc_result['steps'],
                'message': f'계산 결과: {calculation} = {calc_result["result"]}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'계산 중 오류가 발생했습니다: {str(e)}',
                'result': None
            }
    
    def _extract_calculation(self, message: str) -> str:
        """메시지에서 계산식 추출"""
        # 숫자와 연산자 패턴 찾기
        patterns = [
            r'\d+\s*[\+\-\*\/]\s*\d+',  # 기본 연산
            r'\d+\s*\+\s*\d+\s*\+\s*\d+',  # 다중 덧셈
            r'\d+\s*\*\s*\d+\s*\*\s*\d+',  # 다중 곱셈
            r'\(\s*\d+\s*[\+\-\*\/]\s*\d+\s*\)',  # 괄호 연산
            r'\d+\s*\*\*\s*\d+',  # 거듭제곱
            r'sqrt\s*\(\s*\d+\s*\)',  # 제곱근
            r'log\s*\(\s*\d+\s*\)',  # 로그
            r'sin\s*\(\s*\d+\s*\)',  # 사인
            r'cos\s*\(\s*\d+\s*\)',  # 코사인
            r'tan\s*\(\s*\d+\s*\)',  # 탄젠트
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group()
        
        # 한국어 키워드 기반 추출
        korean_patterns = {
            r'(\d+)\s*더하기\s*(\d+)': r'\1 + \2',
            r'(\d+)\s*빼기\s*(\d+)': r'\1 - \2',
            r'(\d+)\s*곱하기\s*(\d+)': r'\1 * \2',
            r'(\d+)\s*나누기\s*(\d+)': r'\1 / \2',
            r'(\d+)\s*의\s*(\d+)\s*제곱': r'\1 ** \2',
            r'(\d+)\s*의\s*제곱근': r'sqrt(\1)',
        }
        
        for pattern, replacement in korean_patterns.items():
            match = re.search(pattern, message)
            if match:
                return re.sub(pattern, replacement, message)
        
        return ""
    
    def _perform_calculation(self, expression: str) -> Dict[str, Any]:
        """실제 계산 수행"""
        try:
            # 안전한 계산을 위해 허용된 함수만 사용
            safe_dict = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'sqrt': math.sqrt,
                'log': math.log,
                'log10': math.log10,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'pi': math.pi,
                'e': math.e
            }
            
            # 표현식 정리
            clean_expression = expression.replace(' ', '')
            
            # 계산 과정 생성
            steps = []
            steps.append(f"원본 수식: {expression}")
            steps.append(f"정리된 수식: {clean_expression}")
            
            # 계산 수행
            result = eval(clean_expression, {"__builtins__": {}}, safe_dict)
            
            # 결과가 정수인 경우 정수로 반환
            if result == int(result):
                final_result = int(result)
                steps.append(f"계산 결과: {final_result}")
            else:
                final_result = round(result, 6)
                steps.append(f"계산 결과: {final_result} (소수점 6자리 반올림)")
            
            return {
                'result': final_result,
                'steps': '\n'.join(steps)
            }
            
        except Exception as e:
            raise ValueError(f"계산 오류: {str(e)}")
    
    def calculate_statistics(self, numbers: List[float]) -> Dict[str, float]:
        """통계 계산"""
        if not numbers:
            return {}
        
        return {
            'mean': statistics.mean(numbers),
            'median': statistics.median(numbers),
            'mode': statistics.mode(numbers) if len(numbers) > 1 else numbers[0],
            'variance': statistics.variance(numbers),
            'std_dev': statistics.stdev(numbers),
            'min': min(numbers),
            'max': max(numbers),
            'sum': sum(numbers),
            'count': len(numbers)
        }
    
    def solve_equation(self, equation: str) -> Dict[str, Any]:
        """간단한 방정식 해결"""
        # 1차 방정식: ax + b = c 형태
        pattern = r'(\d+)x\s*([\+\-])\s*(\d+)\s*=\s*(\d+)'
        match = re.match(pattern, equation)
        
        if match:
            a = float(match.group(1))
            op = match.group(2)
            b = float(match.group(3))
            c = float(match.group(4))
            
            if op == '+':
                x = (c - b) / a
            else:
                x = (c + b) / a
            
            return {
                'equation': equation,
                'solution': x,
                'type': 'linear'
            }
        
        return {
            'status': 'unsupported',
            'message': '지원하지 않는 방정식 형태입니다.'
        }
    
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """단위 변환"""
        conversions = {
            'length': {
                'm': 1,
                'cm': 0.01,
                'mm': 0.001,
                'km': 1000,
                'inch': 0.0254,
                'ft': 0.3048,
                'yd': 0.9144,
                'mile': 1609.34
            },
            'weight': {
                'kg': 1,
                'g': 0.001,
                'mg': 0.000001,
                'lb': 0.453592,
                'oz': 0.0283495
            },
            'temperature': {
                'celsius': 'c',
                'fahrenheit': 'f',
                'kelvin': 'k'
            }
        }
        
        # 길이 변환
        if from_unit in conversions['length'] and to_unit in conversions['length']:
            base_value = value * conversions['length'][from_unit]
            result = base_value / conversions['length'][to_unit]
            return {
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'result': round(result, 6),
                'type': 'length'
            }
        
        # 무게 변환
        elif from_unit in conversions['weight'] and to_unit in conversions['weight']:
            base_value = value * conversions['weight'][from_unit]
            result = base_value / conversions['weight'][to_unit]
            return {
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'result': round(result, 6),
                'type': 'weight'
            }
        
        # 온도 변환
        elif from_unit in conversions['temperature'] and to_unit in conversions['temperature']:
            result = self._convert_temperature(value, from_unit, to_unit)
            return {
                'value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'result': round(result, 2),
                'type': 'temperature'
            }
        
        return {
            'status': 'unsupported',
            'message': '지원하지 않는 단위 변환입니다.'
        }
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """온도 변환"""
        # 섭씨로 변환
        if from_unit == 'fahrenheit':
            celsius = (value - 32) * 5/9
        elif from_unit == 'kelvin':
            celsius = value - 273.15
        else:
            celsius = value
        
        # 목표 단위로 변환
        if to_unit == 'fahrenheit':
            return celsius * 9/5 + 32
        elif to_unit == 'kelvin':
            return celsius + 273.15
        else:
            return celsius
