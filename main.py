from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    # 기본 샘플 풀
    sample_pool = [
        ("System", "채팅에 참여해 스콘즈를 응원하세요!"),
        ("스콘팬1", "오늘 의상 진짜 미쳤다ㅠㅠㅠ"),
        ("김스콘", "실시간으로 보고 있는데 너무 떨려"),
        ("토끼단", "스콘즈 화이팅!! 언제나 응원해"),
        ("모찌", "노래 선곡 미쳤다 진짜"),
        ("별빛스콘", "댓글 읽어주세요 제발요ㅠㅠ"),
        ("체리", "오늘 라이브 레전드 찍네ㅋㅋㅋ")
    ]

    palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"]
    def get_color(name):
        h = 0
        for ch in name:
            h = ord(ch) + ((h << 5) - h)
        return palette[abs(h) % len(palette)]

    # 유저 입력 파라미터 파싱
    chat_list = []
    if users and msgs:
        u_arr = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        m_arr = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]
        for u, m in zip(u_arr, m_arr):
            chat_list.append((u, m))

    if not chat_list:
        chat_list = sample_pool

    # 무한 루프 애니메이션을 위해 2회 연속 배치
    looped_chats = chat_list + chat_list
    total_items = len(chat_list)

    # 1. 배경 이미지
    bg_tag = '<rect width="800" height="350" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_tag = f'<image x="0" y="0" width="800" height="350" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except Exception:
            pass

    # 2. 텍스트 노드 생성 (하단 기준 배치)
    LINE_HEIGHT = 28
    START_Y = 265  # 입력창 바로 위 기준점
    
    text_elements = []
    for i, (u, m) in enumerate(looped_chats):
        y_pos = START_Y + (i * LINE_HEIGHT)
        if u == "System":
            text_elements.append(
                f'<text x="0" y="{y_pos}" class="chat-text" fill="#AAAAAA">System: {m}</text>'
            )
        else:
            col = get_color(u)
            text_elements.append(
                f'<text x="0" y="{y_pos}" class="chat-text">'
                f'<tspan fill="{col}" font-weight="bold">{u}</tspan>'
                f'<tspan fill="#FFFFFF">: {m}</tspan>'
                f'</text>'
            )

    items_svg = "\n    ".join(text_elements)
    
    # 스크롤 거리 및 애니메이션 시간 계산
    scroll_distance = total_items * LINE_HEIGHT
    anim_duration = max(8, total_items * 2.2)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
  <defs>
    <clipPath id="chat-view-area">
      <rect x="20" y="55" width="760" height="225" />
    </clipPath>
    <style>
      .chat-text {{
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', -apple-system, sans-serif;
        font-size: 14px;
      }}
      @keyframes autoChatScroll {{
        0% {{
          transform: translateY(0px);
        }}
        100% {{
          transform: translateY(-{scroll_distance}px);
        }}
      }}
      #chatScrollGroup {{
        animation: autoChatScroll {anim_duration}s linear infinite;
      }}
    </style>
  </defs>

  <!-- 1. 배경 -->
  {bg_tag}
  <rect width="800" height="350" fill="#000000" opacity="0.45"/>

  <!-- 2. 스크롤 채팅 영역 (CSS 무한 롤링) -->
  <g clip-path="url(#chat-view-area)">
    <g id="chatScrollGroup" transform="translate(20, 0)">
    {items_svg}
    </g>
  </g>

  <!-- 3. 상단 LIVE 배지 (고정) -->
  <g transform="translate(20, 18)">
    <rect width="46" height="22" rx="4" fill="#FF2D55"/>
    <text x="10" y="15" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="11px">LIVE</text>
  </g>

  <!-- 4. 하단 입력창 UI (고정) -->
  <g transform="translate(20, 290)">
    <rect width="760" height="42" rx="21" fill="#202020" opacity="0.85"/>
    <text x="22" y="26" fill="#888888" font-family="'Malgun Gothic', sans-serif" font-size="13px">채팅에 참여하세요...</text>
    <text x="725" y="27" fill="#FF5A78" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="16px">♥</text>
  </g>
</svg>'''

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )
