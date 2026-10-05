from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    if not users or not msgs:
        user_list = ["System", "스콘팬1", "김스콘", "토끼단"]
        msg_list = [
            "채팅에 참여해 스콘즈를 응원하세요!",
            "오늘 의상 진짜 미쳤다ㅠㅠㅠ",
            "실시간으로 보고 있는데 너무 떨려",
            "스콘즈 화이팅!! 언제나 응원해"
        ]
    else:
        user_list = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        msg_list = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]

    # 배경 이미지(bg.png) 처리
    bg_svg_tag = '<rect width="800" height="350" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_svg_tag = f'<image x="0" y="0" width="800" height="350" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except:
            pass

    # 순수 SVG 구조 (외부 제약 없이 플랫폼과 브라우저에서 100% 렌더링 보장)
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
  <defs>
    <clipPath id="chat-view-area">
      <rect x="20" y="55" width="760" height="210" />
    </clipPath>
    <style>
      @keyframes fadeSlide {{
        0% {{ opacity: 0; transform: translateY(12px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}
      .chat-line {{
        animation: fadeSlide 0.3s ease-out forwards;
      }}
    </style>
  </defs>

  <!-- 1. 배경 이미지 -->
  {bg_svg_tag}
  
  <!-- 배경 어둡게 오버레이 -->
  <rect width="800" height="350" fill="#000000" rx="12" opacity="0.6"/>

  <!-- 2. 상단 LIVE 배지 -->
  <g transform="translate(20, 18)">
    <rect width="46" height="22" rx="4" fill="#FF2D55"/>
    <text x="9" y="15" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="11px">LIVE</text>
    <circle cx="70" cy="11" r="4" fill="#FFFFFF"/>
    <text x="82" y="15" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="12px">1.2M</text>
  </g>

  <!-- 3. 스크롤 채팅 영역 -->
  <g clip-path="url(#chat-view-area)">
    <g transform="translate(25, 0)">
'''

    palette = ["#FF6E6E", "#6EE273", "#73BEFF", NumericColor if False else "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"]
    
    # 전달받은 데이터 렌더링
    display_users = user_list[-6:]
    display_msgs = msg_list[-6:]
    start_y = 90
    
    for i, (u, m) in enumerate(zip(display_users, display_msgs)):
        y_pos = start_y + (i * 32)
        if u == "System":
            svg_content += f'      <text x="0" y="{y_pos}" fill="#AAAAAA" font-family="\'Malgun Gothic\', sans-serif" font-size="14px" class="chat-line">System: {m}</text>\n'
        else:
            color_idx = sum(ord(c) for c in u) % len(palette)
            color = palette[color_idx]
            svg_content += f'''      <text x="0" y="{y_pos}" font-family="'Malgun Gothic', sans-serif" font-size="14px" class="chat-line">
        <tspan fill="{color}" font-weight="bold">{u}</tspan>
        <tspan fill="#FFFFFF">: {m}</tspan>
      </text>\n'''

    svg_content += f'''    </g>
  </g>

  <!-- 4. 하단 입력창 UI -->
  <g transform="translate(20, 290)">
    <rect width="760" height="42" rx="21" fill="#202020" opacity="0.85"/>
    <text x="22" y="26" fill="#888888" font-family="'Malgun Gothic', sans-serif" font-size="13px">채팅에 참여하세요...</text>
    <text x="725" y="27" fill="#FF5A78" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="16px">♥</text>
  </g>
</svg>'''

    return Response(content=svg_content, media_type="image/svg+xml")
