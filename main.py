from fastapi import FastAPI, Response
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
import os

app = FastAPI()

# 닉네임을 다채롭고 예쁘게 보여줄 색상 팔레트 (유튜브 스타일 컬러들)
COLOR_PALETTE = [
    (255, 110, 110),  # 코랄 핑크
    (110, 220, 115),  # 연두빛
    (115, 190, 255),  # 하늘빛
    (255, 200, 80),   # 노랑
    (220, 130, 255),  # 연보라
    (80, 230, 210),   # 민트
    (255, 150, 80)    # 주황
]

def get_color_for_name(name):
    # 이름 글자들의 코드값을 이용해 유저마다 고정되면서도 다양한 색상 선택
    return COLOR_PALETTE[sum(ord(c) for c in name) % len(COLOR_PALETTE)]

@app.get("/")
def generate_chat_image(users: str, msgs: str):
    user_list = [u.strip() for u in users.split(",") if u.strip()]
    msg_list = [m.strip() for m in msgs.split(",") if m.strip()]
    
    # 토큰 한계 등으로 채팅이 부족할 경우 System 안내 문구로 채우기
    while len(user_list) < 3 or len(msg_list) < 3:
        user_list.append("System")
        msg_list.append("채팅에 참여해 스콘즈를 응원하세요!")
        
    width = 600
    chat_height = len(user_list) * 32
    height = 90 + chat_height + 50
    
    # 배경 이미지 불러오기 (없으면 어두운 단색 배경)
    if os.path.exists("bg.png"):
        try:
            bg = Image.open("bg.png").convert("RGBA")
            bg = bg.resize((width, height))
            darken = Image.new("RGBA", (width, height), (0, 0, 0, 180))
            image = Image.alpha_composite(bg, darken)
        except:
            image = Image.new("RGBA", (width, height), (15, 15, 15, 245))
    else:
        image = Image.new("RGBA", (width, height), (15, 15, 15, 245))
        
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("malgun.ttf", 13)
        font_bold = ImageFont.truetype("malgunbd.ttf", 13)
        font_small = ImageFont.truetype("malgun.ttf", 11)
    except:
        font = ImageFont.load_default()
        font_bold = font
        font_small = font
        
    # --- [상단 LIVE 방송국 UI 바] ---
    draw.rectangle([0, 0, width, 45], fill=(25, 25, 25, 200))
    draw.rounded_rectangle([15, 12, 55, 32], radius=4, fill=(204, 0, 0))
    draw.text((23, 15), "LIVE", fill=(255, 255, 255), font=font_bold)
    
    # --- [실시간 채팅 목록 (다채로운 닉네임 컬러 적용)] ---
    y_offset = 55
    for u, m in zip(user_list, msg_list):
        username = urllib.parse.unquote(u).strip()
        message = urllib.parse.unquote(m).strip()
        
        if username == "System":
            text_full = f"System: {message}"
            draw.text((15, y_offset), text_full, fill=(170, 170, 170), font=font)
        else:
            # 유저별 다채로운 고유 색상 부여
            name_color = get_color_for_name(username)
            draw.text((15, y_offset), username, fill=name_color, font=font_bold)
            
            name_w = font_bold.getlength(username) if hasattr(font_bold, 'getlength') else len(username) * 7
            draw.text((15 + name_w + 8, y_offset), f": {message}", fill=(255, 255, 255), font=font)
            
        y_offset += 28
        
    # --- [하단 채팅 입력창] ---
    input_box_y = height - 42
    draw.rounded_rectangle([15, input_box_y, width - 15, height - 10], radius=18, fill=(30, 30, 30, 200))
    draw.text((30, input_box_y + 8), "채팅에 참여하세요...", fill=(140, 140, 140), font=font_small)
    draw.text((width - 45, input_box_y + 7), "♥", fill=(255, 90, 120), font=font_bold)

    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
