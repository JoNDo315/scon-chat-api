from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

COLOR_PALETTE = [
    "#FF6E6E",  # 코랄 핑크
    "#6EE273",  # 연두빛
    "#73BEFF",  # 하늘빛
    "#FFC850",  # 노랑
    "#DC82FF",  # 연보라
    "#50E6D2",  # 민트
    "#FF9650"   # 주황
]

def get_color_for_name(name):
    return COLOR_PALETTE[sum(ord(c) for c in name) % len(COLOR_PALETTE)]

@app.get("/")
def generate_svg_chat(users: str = None, msgs: str = None):
    # 파라미터가 없을 때 출력될 기본 스콘즈 응원 세팅 (다른 세계관 이름 배제)
    if not users or not msgs:
        user_list = ["System", "금수단", "아뜨", "루모리", "레인이", "무찌", "지푸리", "몽땅이]
        msg_list = [
            "채팅에 참여해 스콘즈를 응원하세요!",
            "스콘즈 오늘 무대 기대할게요!",
            "와 실시간으로 보는 중ㅠㅠ",
            "스콘즈 화이팅!!"
        ]
    else:
        user_list = [u.strip() for u in users.split(",") if u.strip()]
        msg_list = [m.strip() for m in msgs.split(",") if m.strip()]
        
        while len(user_list) < 4 or len(msg_list) < 4:
            user_list.append("System")
            msg_list.append("채팅에 참여해 스콘즈를 응원하세요!")
            
    max_visible = 7
    if len(user_list) > max_visible:
        user_list = user_list[-max_visible:]
        msg_list = msg_list[-max_visible:]
        
    width = 600
    chat_height = len(user_list) * 28
    height = 80 + chat_height + 50
    
    bg_svg_tag = ""
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_svg_tag = f'<image x="0" y="0" width="{width}" height="{height}" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except:
            pass
            
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .chat-font {{ font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; font-size: 13px; }}
    .bold {{ font-weight: bold; }}
    .system-text {{ fill: #AAAAAA; }}
    .placeholder {{ fill: #888888; font-size: 11px; }}
    @keyframes smoothScroll {{
      0% {{ transform: translateY(28px); opacity: 0; }}
      100% {{ transform: translateY(0px); opacity: 1; }}
    }}
    .scroll-area {{
      animation: smoothScroll 0.4s cubic-bezier(0.1, 0.9, 0.2, 1) forwards;
    }}
  </style>
'''

    if bg_svg_tag:
        svg_content += f'  {bg_svg_tag}\n'
        svg_content += f'  <rect width="{width}" height="{height}" fill="#000000" opacity="0.6"/>\n'
    else:
        svg_content += f'  <rect width="{width}" height="{height}" fill="#141414"/>\n'

    # 상단 LIVE 배지
    svg_content += '''  <g transform="translate(15, 15)">
    <rect width="40" height="20" rx="4" fill="#CC0000"/>
    <text x="8" y="14" fill="#FFFFFF" class="chat-font bold" font-size="11">LIVE</text>
  </g>
'''

    # 채팅 목록 영역
    svg_content += '  <g class="scroll-area">\n'
    y = 65
    for u, m in zip(user_list, msg_list):
        username = urllib.parse.unquote(u).strip()
        message = urllib.parse.unquote(m).strip()
        
        if username == "System":
            svg_content += f'    <text x="15" y="{y}" class="chat-font system-text">System: {message}</text>\n'
        else:
            color = get_color_for_name(username)
            svg_content += f'    <text x="15" y="{y}" class="chat-font bold" fill="{color}">{username}<tspan fill="#FFFFFF">: {message}</tspan></text>\n'
        y += 28
    svg_content += '  </g>\n'

    # 하단 입력창
    input_y = height - 42
    svg_content += f'''  <g transform="translate(15, {input_y})">
    <rect width="{width - 30}" height="32" rx="16" fill="#202020" opacity="0.85"/>
    <text x="15" y="20" class="chat-font placeholder">채팅에 참여하세요...</text>
    <text x="{width - 60}" y="21" fill="#FF5A78" class="chat-font bold">♥</text>
  </g>
'''
    svg_content += '</svg>'

    return Response(content=svg_content, media_type="image/svg+xml")
