# AWS에서 Stable Diffusion을 위한 GPU 서버 설정 가이드

## AWS EC2 GPU 인스턴스 추천

### 최소 사양 (가성비)
- **인스턴스 타입**: `g4dn.xlarge`
- **GPU**: NVIDIA T4 (16GB VRAM)
- **vCPU**: 4
- **메모리**: 16GB
- **스토리지**: 최소 50GB SSD
- **예상 비용**: 시간당 약 $0.5~0.7 (리전에 따라 다름)
- **예상 비용**: 대략 하루 ~2만원, 1주일 14만원, 한달 60만원

### 중간 사양 (권장)
- **인스턴스 타입**: `g5.xlarge`
- **GPU**: NVIDIA A10G (24GB VRAM)
- **vCPU**: 4
- **메모리**: 16GB
- **스토리지**: 최소 100GB SSD
- **예상 비용**: 시간당 약 $1.0~1.3

### 고사양 (대규모 모델용)
- **인스턴스 타입**: `p3.2xlarge`
- **GPU**: NVIDIA V100 (16GB VRAM)
- **vCPU**: 8
- **메모리**: 61GB
- **스토리지**: 최소 100GB SSD
- **예상 비용**: 시간당 약 $3.0~3.8

## 설정 방법

1. **AMI 선택**: 
   - "Deep Learning AMI GPU PyTorch" AMI 선택 (NVIDIA 드라이버와 CUDA가 사전 설치됨)
   - 또는 Amazon Linux 2/Ubuntu에 직접 환경 설정 가능

2. **스토리지 구성**:
   - 루트 볼륨: 최소 50GB (OS + 패키지)
   - 추가 볼륨 (선택사항): 100GB+ (데이터셋 및 모델 저장용)

3. **보안 그룹**:
   - SSH (22번 포트) 접속 허용
   - 필요한 경우 웹 서버 포트(80, 443) 또는 Jupyter 포트(8888)

4. **비용 관리**:
   - 사용하지 않을 때는 반드시 인스턴스 중지 (GPU 인스턴스는 유휴 상태에서도 비용이 발생)
   - 스팟 인스턴스 고려 (최대 70% 할인, 단 작업 중 종료 위험 있음)

## 접속 및 환경 설정

1. **SSH로 접속**:
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

2. **가상 환경 생성**:
   ```bash
   # 이미 PyTorch 환경이 있는 AMI 사용 시 필요 없음
   conda create -n stable-diffusion python=3.10
   conda activate stable-diffusion
   ```

3. **필요 패키지 설치**:
   ```bash
   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
   pip install diffusers transformers accelerate safetensors
   ```

4. **코드 다운로드**:
   ```bash
   # git 사용
   git clone https://your-repository-url.git
   
   # 또는 SCP로 로컬에서 파일 전송
   scp -i your-key.pem -r local-folder ec2-user@your-instance-ip:~/
   ```

## 사용 팁

1. **VRAM 사용량 모니터링**:
   ```bash
   watch -n 1 nvidia-smi
   ```

2. **원격 실행 후 연결 유지**:
   ```bash
   # tmux 또는 screen 사용 (연결이 끊겨도 작업 유지)
   tmux new -s diffusion
   # 작업 실행 후 Ctrl+B, D로 세션 유지하며 분리
   # 재접속: tmux attach -t diffusion
   ```

3. **결과 다운로드**:
   ```bash
   # 로컬 PC에서 실행
   scp -i your-key.pem -r ec2-user@your-instance-ip:~/model_outputs ./
   ```

## 참고 사항

- **비용 절감**: 필요한 작업만 수행하고 인스턴스를 중지하거나 종료하세요.
- **EBS 볼륨**: 인스턴스를 종료해도 EBS 볼륨은 유지되도록 설정하면 다음에 새 인스턴스에 연결할 수 있습니다.
- **리전 선택**: 가장 가까운 리전을 선택하면 지연 시간이 줄어듭니다 (한국의 경우 서울 리전).
- **Jupyter 설정**: 노트북으로 작업하려면 Jupyter를 설정하고 SSH 터널링으로 연결하는 것이 편리합니다.

NVIDIA T4가 장착된 g4dn.xlarge는 Stable Diffusion 모델을 실행하는 데 적합한 가성비 옵션입니다. 더 큰 모델이나 더 빠른 생성을 원한다면 g5.xlarge나 p3.2xlarge를 고려하세요.
