import subprocess
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='Stable Diffusion 모델 실행')
    parser.add_argument('model', type=str, choices=['all', 'sd_v1_5', 'sd_v2_1', 'dreamlike', 'openjourney', 'redshift', 'analog'], 
                        help='실행할 모델 선택 (또는 "all"로 모두 실행)')
    args = parser.parse_args()
    
    models = {
        'sd_v1_5': 'model_scripts/sd_v1_5.py',
        'sd_v2_1': 'model_scripts/sd_v2_1.py',
        'dreamlike': 'model_scripts/dreamlike.py',
        'openjourney': 'model_scripts/openjourney.py',
        'redshift': 'model_scripts/redshift.py',
        'analog': 'model_scripts/analog.py'
    }
    
    if args.model == 'all':
        print("모든 모델을 순차적으로 실행합니다.")
        for model_name, script_path in models.items():
            print(f"\n== {model_name} 모델 실행 중... ==")
            run_script(script_path)
    else:
        if args.model in models:
            print(f"{args.model} 모델을 실행합니다.")
            run_script(models[args.model])
        else:
            print(f"알 수 없는 모델: {args.model}")
            sys.exit(1)

def run_script(script_path):
    try:
        result = subprocess.run([sys.executable, script_path], check=True)
        if result.returncode == 0:
            print(f"스크립트 {script_path} 실행 성공")
        else:
            print(f"스크립트 {script_path} 실행 실패 (코드: {result.returncode})")
    except subprocess.CalledProcessError as e:
        print(f"스크립트 실행 중 오류 발생: {e}")
    except Exception as e:
        print(f"예기치 않은 오류: {e}")

if __name__ == "__main__":
    main()
