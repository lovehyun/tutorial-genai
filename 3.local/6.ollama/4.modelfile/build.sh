#!/usr/bin/env bash
# 두 커스텀 모델을 한 번에 빌드한다 (= ollama create).
# 실행:  bash build.sh
set -e
cd "$(dirname "$0")"

echo "▶ qwen-korean  (FROM qwen3.5:4b)"
ollama create qwen-korean   -f Modelfile.korean

echo "▶ gemma4-korean (FROM gemma4:e4b)"
ollama create gemma4-korean -f Modelfile.reasoning

echo
echo "✅ 완료. 확인:  ollama list | grep -E 'qwen-korean|gemma4-korean'"
echo "   실행 예:    ollama run qwen-korean"
echo "   삭제:       ollama rm qwen-korean gemma4-korean"
