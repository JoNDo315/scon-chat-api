from fastapi import FastAPI, Response
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

app = FastAPI()

@app.get("/")
def generate_chat_image(users: str, msgs: str):
    user_list = users.split(",")
    msg_list = msgs.split(",")
    
    # 1. 유튜브 라이브 플레이어 전체 크기 설정 (가로 600px, 세로 가변)
    width = 600
    chat_height = len(user_list) * 32
    height = 90 + chat_height + 50  # 상단바(45) + 채팅들 + 하단입력창(50)
    
    # 2. 전체 배경 (어두운 유튜브 플레이어 배경 색상)
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
        
    # --- [상단 LIVE 방송국 UI 바 그리기] ---
    # 상단바 배경
    draw.rectangle([0, 0, width, 45], fill=(25, 25, 25, 255))
    # 빨간색 LIVE 아이콘
    draw.rounded_rectangle([15, 12, 50, 32], radius=4, fill=(204, 0, 0))
    draw.text((22, 15), "LIVE", fill=(255, 255, 255), font=font_bold)
    # 시청자 수 (1.2M)
    draw.text((62, 16), "●  1.2M", fill=(200, 200, 200), font=font_small)
    
    # --- [중간 실시간 채팅 목록 그리기] ---
    y_offset = 55
    for u, m in zip(user_list, msg_list):
        username = urllib.parse.unquote(u).strip()
        message = urllib.parse.unquote(m).strip()
        
        # 닉네임과 메시지 출력 (시스템 메시지는 회색, 일반 유저는 흰색)
        if username == "System":
            text_full = f"System: {message}"
            draw.text((15, y_offset), text_full, fill=(170, 170, 170), font=font)
        else:
            # 닉네임은 조금 밝게, 대사는 흰색으로
            draw.text((15, y_offset), username, fill=(255, 120, 120) if "엄" in username else (200, 200, 200), font=font_bold)
            # 닉네임 길이에 따라 대사 시작 위치 조절
            name_w = font_bold.getlength(username) if hasattr(font_bold, 'getlength') else len(username) * 7
            draw.text((15 + name_w + 8, y_offset), f": {message}", fill=(255, 255, 255), font=font)
            
        y_offset += 28
        
    # --- [하단 채팅 입력창 UI 그리기] ---
    input_box_y = height - 42
    draw.rounded_rectangle([15, input_box_y, width - 15, height - 10], radius=18, fill=(40, 40, 40))
    draw.text((30, input_box_y + 8), "채팅에 참여하세요...", fill=(140, 140, 140), font=font_small)
    # 우측 하트 아이콘 모양 포인트
    draw.text((width - 45, input_box_y + 7), "♥", fill=(255, 90, 120), font=font_bold)

    # 3. 이미지 저장 및 응답
    import io
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")
    
