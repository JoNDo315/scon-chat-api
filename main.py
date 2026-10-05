 from fastapi import FastAPI, Response
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
import os

app = FastAPI()

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
    return COLOR_PALETTE[sum(ord(c) for c in name) % len(COLOR_PALETTE)]

@app.get("/")
def generate_chat_image(users: str, msgs: str):
    user_list = [u.strip() for u in users.split(",") if u.strip()]
    msg_list = [m.strip() for m in msgs.split(",") if m.strip()]
    
    while len(user_list) < 3 or len(msg_list) < 3:
        user_list.append("System")
        msg_list.append("채팅에 참여해 스콘즈를 응원하세요!")
        
    width = 600
    chat_height = len(user_list) * 35
    height = 95 + chat_height + 50
    
    # 배경 이미지 불러오기 및 어두운 필터 합성
    if os.path.exists("bg.png"):
        try:
            bg = Image.open("bg.png").convert("RGBA")
            bg = bg.resize((width, height))
            darken = Image.new("RGBA", (width, height), (15, 15, 15, 210)) # 투명도 조절로 배경이 은은하게 보이도록 설정
            image = Image.alpha_composite(bg, darken)
        except:
            image = Image.new("RGBA", (width, height), (20, 20, 20, 255))
    else:
        image = Image.new("RGBA", (width, height), (20, 20, 20, 255))
        
    draw = ImageDraw.Draw(image)
    
    # 폰트 로드 (기본 폰트 안전 장치)
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    # --- [상단 LIVE 방송국 UI 바] ---
    draw.rectangle([0, 0, width, 40], fill=(25, 25, 25))
    draw.rounded_rectangle([15, 10, 50, 30], radius=4, fill=(204, 0, 0))
    draw.text((21, 13), "LIVE", fill=(255, 255, 255))
    
    # --- [실시간 채팅 목록] ---
    y_offset = 55
    for u, m in zip(user_list, msg_list):
        username = urllib.parse.unquote(u).strip()
        message = urllib.parse.unquote(m).strip()
        
        if username == "System":
            text_full = f"System: {message}"
            draw.text((15, y_offset), text_full, fill=(170, 170, 170))
        else:
            name_color = get_color_for_name(username)
            draw.text((15, y_offset), username, fill=name_color)
            
            name_w = len(username) * 7
            draw.text((15 + name_w + 8, y_offset), f": {message}", fill=(255, 255, 255))
            
        y_offset += 32
        
    # --- [하단 채팅 입력창] ---
    input_box_y = height - 42
    draw.rounded_rectangle([15, input_box_y, width - 15, height - 10], radius=18, fill=(35, 35, 35))
    draw.text((30, input_box_y + 8), "채팅에 참여하세요...", fill=(150, 150, 150))
    draw.text((width - 45, input_box_y + 7), "♥", fill=(255, 90, 120))

    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
