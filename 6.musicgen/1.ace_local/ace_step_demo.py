"""
ACE-Step 음악 생성 예제
- ACE-Step v1 API를 사용하여 텍스트 + 가사로 음악을 생성합니다.
- 설치: pip install ace-step
- 필요 VRAM: 8GB+ (cpu_offload 사용 시)
"""
import os
import datetime

# ── ACE-Step v1 기본 사용법 ──


def demo_basic():
    """기본 텍스트→음악 생성"""
    from acestep.pipeline import ACEStepPipeline

    print("=" * 50)
    print("  ACE-Step 기본 음악 생성")
    print("=" * 50)

    # 파이프라인 로드 (첫 실행 시 모델 자동 다운로드)
    print("\n[1] 모델 로드 중...")
    pipeline = ACEStepPipeline.from_pretrained(
        "ACE-Step/ACE-Step-v1-3.5B",
        device_id=0,
        bf16=True,
        torch_compile=True,
        cpu_offload=True,  # 8GB VRAM에서도 동작
    )
    print("  모델 로드 완료!")

    # ── 예제 1: K-Pop 스타일 ──
    print("\n[2] K-Pop 스타일 음악 생성 중...")
    audio_kpop = pipeline.text2music(
        prompt="upbeat K-pop, catchy synth melody, female vocal, dance beat, 120 BPM",
        lyrics="""[verse]
빛나는 별처럼 우리 함께 달려가
멈추지 마 이 순간을 놓치지 마

[chorus]
Let's go, let's go, 더 높이 날아가
모두 함께 소리쳐 la la la la""",
        duration=30,
        infer_steps=27,
        guidance_scale=15.0,
        seed=42,
    )

    os.makedirs("output", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/kpop_{timestamp}.wav"

    # 오디오 저장
    import soundfile as sf
    sf.write(output_path, audio_kpop.T, 44100)
    print(f"  저장 완료: {output_path}")

    # ── 예제 2: Lo-fi 힙합 (기악) ──
    print("\n[3] Lo-fi 힙합 기악 생성 중...")
    audio_lofi = pipeline.text2music(
        prompt="lo-fi hip hop, chill piano, vinyl crackle, jazzy chords, 85 BPM",
        lyrics="[instrumental]",
        duration=60,
        infer_steps=27,
        guidance_scale=15.0,
        seed=123,
    )

    output_path2 = f"output/lofi_{timestamp}.wav"
    sf.write(output_path2, audio_lofi.T, 44100)
    print(f"  저장 완료: {output_path2}")

    # ── 예제 3: 록 발라드 (한국어 가사) ──
    print("\n[4] 록 발라드 생성 중...")
    audio_rock = pipeline.text2music(
        prompt="emotional rock ballad, electric guitar, powerful drums, male vocal, 75 BPM",
        lyrics="""[intro]
(guitar solo)

[verse]
어두운 밤을 걸어가며
너를 떠올려 다시 한번

[chorus]
잊지 못할 그 날의 기억
여전히 내 맘속에 남아있어

[outro]
(fade out)""",
        duration=45,
        infer_steps=60,           # 높은 스텝 = 더 높은 품질
        guidance_scale=15.0,
        guidance_scale_text=15.0,
        guidance_scale_lyric=15.0,
        seed=456,
    )

    output_path3 = f"output/rock_ballad_{timestamp}.wav"
    sf.write(output_path3, audio_rock.T, 44100)
    print(f"  저장 완료: {output_path3}")

    print("\n" + "=" * 50)
    print("  모든 생성 완료!")
    print("=" * 50)


# ── 고급 기능 데모 ──


def demo_advanced():
    """고급 기능: Retake, Repaint, Edit, Extend"""
    from acestep.pipeline import ACEStepPipeline

    print("=" * 50)
    print("  ACE-Step 고급 기능 데모")
    print("=" * 50)

    pipeline = ACEStepPipeline.from_pretrained(
        "ACE-Step/ACE-Step-v1-3.5B",
        device_id=0,
        bf16=True,
        torch_compile=True,
        cpu_offload=True,
    )

    # 먼저 기본 곡 생성
    print("\n[1] 기본 곡 생성...")
    audio = pipeline.text2music(
        prompt="acoustic folk, warm guitar, soft vocal, 100 BPM",
        lyrics="""[verse]
Morning light through the window pane
A brand new day begins again""",
        duration=30,
        infer_steps=27,
        guidance_scale=15.0,
        seed=42,
    )

    import soundfile as sf
    os.makedirs("output", exist_ok=True)
    base_path = "output/folk_base.wav"
    sf.write(base_path, audio.T, 44100)
    print(f"  기본 곡 저장: {base_path}")

    # Retake — 같은 설정으로 변형 생성
    print("\n[2] Retake (변형 생성)...")
    audio_retake = pipeline.retake(
        source_audio=base_path,
        retake_variance=0.5,     # 0.0(동일) ~ 1.0(완전히 다름)
        guidance_scale=15.0,
    )
    sf.write("output/folk_retake.wav", audio_retake.T, 44100)
    print("  변형 저장: output/folk_retake.wav")

    # Repaint — 특정 구간만 재생성
    print("\n[3] Repaint (10~20초 구간 재생성)...")
    audio_repaint = pipeline.repaint(
        source_audio=base_path,
        repaint_start_time=10,
        repaint_end_time=20,
        new_prompt="add electric guitar solo here",
    )
    sf.write("output/folk_repaint.wav", audio_repaint.T, 44100)
    print("  부분 재생성 저장: output/folk_repaint.wav")

    # Edit — 스타일 변경
    print("\n[4] Edit (스타일을 재즈로 변경)...")
    audio_edit = pipeline.edit(
        source_audio=base_path,
        target_prompt="smooth jazz, saxophone, piano",
        new_lyrics="""[verse]
Morning light through the window pane
A jazzy day begins again""",
        n_min=0,
        n_max=1000,
    )
    sf.write("output/folk_to_jazz.wav", audio_edit.T, 44100)
    print("  스타일 편집 저장: output/folk_to_jazz.wav")

    # Extend — 뒤에 30초 연장
    print("\n[5] Extend (30초 연장)...")
    audio_extend = pipeline.extend(
        source_audio=base_path,
        extend_left=0,
        extend_right=30,
    )
    sf.write("output/folk_extended.wav", audio_extend.T, 44100)
    print("  연장 저장: output/folk_extended.wav")

    print("\n" + "=" * 50)
    print("  고급 기능 데모 완료!")
    print("=" * 50)


# ── 학습 포인트 ──


def print_learning_points():
    print("\n" + "=" * 50)
    print("  [ 학습 포인트 ]")
    print("=" * 50)
    print("""
1. 프롬프트 구조:
   - prompt: 장르, 악기, 분위기, BPM 등 스타일 태그
   - lyrics: [verse], [chorus], [instrumental] 등 구간 태그 + 가사
   → 두 가지를 분리하여 스타일과 내용을 독립적으로 제어

2. 품질 제어:
   - infer_steps: 높을수록 품질 향상 (27=빠른, 60=고품질)
   - guidance_scale: 높을수록 프롬프트에 충실 (15.0 권장)
   - seed: 동일 시드 = 동일 결과 (재현성)

3. 고급 편집 기능:
   - Retake: variance로 원본 대비 변형 정도 조절
   - Repaint: 특정 시간 구간만 재생성 (나머지 유지)
   - Edit: 스타일/가사를 바꾸면서 전체 구조 유지
   - Extend: 앞뒤로 자연스럽게 연장

4. VRAM 최적화:
   - cpu_offload=True: 8GB GPU에서도 동작
   - bf16=True: 메모리 절약 + 속도 향상
   - torch_compile=True: 추론 속도 최적화

5. Diffusion 기반 음악 생성:
   - 이미지 생성의 Stable Diffusion과 유사한 원리
   - 노이즈 → 점진적 디노이징 → 오디오
   - guidance_scale로 조건부 생성 강도 조절
""")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "advanced":
        demo_advanced()
    else:
        demo_basic()

    print_learning_points()
