from PIL import Image, ImageDraw

# 원본 이미지 크기와 동일한 빈 RGBA 이미지 생성
with Image.open("DATA/generated_image.png") as base_img:
    width, height = base_img.size
    mask = Image.new("L", (width, height), 0)  # "L" 모드는 흑백

# Draw 객체 생성
draw = ImageDraw.Draw(mask)

# 편집할 영역 설정 (여기서는 예제로 사각형을 그립니다)
# 이 부분을 원하는 편집 영역으로 수정하세요
edit_area = (width//4, height//4, 3*width//4, 3*height//4)
draw.rectangle(edit_area, fill=255)  # 흰색으로 채우기

# 마스크 이미지 저장
mask.save("DATA/mask.png")

# 마스크 이미지 표시 (선택 사항)
mask.show()
