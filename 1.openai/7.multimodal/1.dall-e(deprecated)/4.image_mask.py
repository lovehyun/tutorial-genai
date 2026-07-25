# DALL-E 이미지 생성 - 4단계: 편집용 마스크 만들기
# pip install pillow
#
# 3단계까지는 '새 이미지 생성'이었다. 4·5단계는 '기존 이미지 편집(인페인팅)'이다.
#
# 인페인팅 = 이미지의 '일부 영역만' AI로 새로 그리는 것.
#   어느 영역을 바꿀지 알려주는 흑백 이미지가 '마스크'다.
#   이 단계: 마스크를 만들어 DATA/mask.png 로 저장한다 (5단계에서 이 마스크를 사용).
#
# 먼저 1단계를 실행해 DATA/generated_image.png 가 있어야 한다 (크기를 맞추기 위함).

from PIL import Image, ImageDraw

# 원본과 '같은 크기'의 마스크를 만들어야 한다 → 원본에서 크기를 읽어온다
with Image.open('DATA/generated_image.png') as base_img:
    width, height = base_img.size

# [관전 포인트] 마스크는 흑백("L") 이미지다
#   검은색(0)  = 그대로 유지할 영역
#   흰색(255) = AI가 새로 그릴 영역
mask = Image.new('L', (width, height), 0)   # 전체를 검은색으로 시작
draw = ImageDraw.Draw(mask)

# 가운데 사각형 영역을 흰색으로 → 이 부분만 편집 대상이 된다
edit_area = (width // 4, height // 4, width * 3 // 4, height * 3 // 4)
draw.rectangle(edit_area, fill=255)

mask.save('DATA/mask.png')
print('마스크 저장 완료: DATA/mask.png')
