from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def generate_svg_overlay(users: str = None, msgs: str = None):
    # 파라미터가 없을 때는 더미 예시 없이 완전히 빈 리스트로 처리
    if not users or not msgs:
        user_list = []
        msg_list = []
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

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
  <script></script>
  <defs>
    <clipPath id="chat-view-area">
      <rect x="0" y="50" width="800" height="210" />
    </clipPath>
  </defs>

  <!-- 1. 배경 -->
  {bg_svg_tag}
  
  <!-- 배경 어둡게 -->
  <rect width="800" height="350" fill="#000000" opacity="0.55"/>

  <!-- 2. 스크롤 채팅 영역 -->
  <g clip-path="url(#chat-view-area)">
    <g id="chat-container">
'''

    palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"]
    
    # 전달받은 실시간 데이터만 정확하게 렌더링 (최대 6개)
    if user_list and msg_list:
        start_y = 90
        display_users = user_list[-6:]
        display_msgs = msg_list[-6:]
        for i, (u, m) in enumerate(zip(display_users, display_msgs)):
            y_pos = start_y + (i * 32)
            if u == "System":
                svg_content += f'      <text x="25" y="{y_pos}" fill="#AAAAAA" font-family="Malgun Gothic, sans-serif" font-size="14px">System: {m}</text>\n'
            else:
                color_idx = sum(ord(c) for c in u) % len(palette)
                color = palette[color_idx]
                svg_content += f'      <text x="25" y="{y_pos}" font-family="Malgun Gothic, sans-serif" font-size="14px"><tspan fill="{color}" font-weight="bold">{u}</tspan><tspan fill="#FFFFFF">: {m}</tspan></text>\n'

    svg_content += '''    </g>
  </g>

  <!-- 3. 상단 LIVE 배지 -->
  <g transform="translate(20, 20)">
    <rect width="46" height="22" rx="4" fill="#FF2D55"/>
    <text x="9" y="15" fill="#FFFFFF" font-family="Malgun Gothic, sans-serif" font-weight="bold" font-size="11px">LIVE</text>
    <circle cx="70" cy="11" r="4" fill="#FFFFFF"/>
    <text x="82" y="15" fill="#FFFFFF" font-family="Malgun Gothic, sans-serif" font-weight="bold" font-size="12px">1.2M</text>
  </g>

  <!-- 4. 하단 입력창 UI -->
  <g transform="translate(20, 290)">
    <rect width="760" height="40" rx="20" fill="#202020" opacity="0.85"/>
    <text x="20" y="25" fill="#888888" font-family="Malgun Gothic, sans-serif" font-size="13px">채팅에 참여하세요...</text>
    <text x="725" y="26" fill="#FF5A78" font-family="Malgun Gothic, sans-serif" font-weight="bold" font-size="16px">♥</text>
  </g>
</svg>'''

    return Response(content=svg_content, media_type="image/svg+xml")
