from fastapi import FastAPI, Response
import urllib.parse
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
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

    chat_list = []
    if users and msgs:
        u_arr = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        m_arr = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]
        for u, m in zip(u_arr, m_arr):
            chat_list.append((u, m))

    if not chat_list:
        chat_list = sample_pool

    total_items = len(chat_list)
    # 완벽한 3배수 순환 루프
    looped_chats = chat_list + chat_list + chat_list

    # 1. 배경 이미지
    bg_tag = '<rect width="800" height="350" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_tag = f'<image x="0" y="0" width="800" height="350" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except Exception:
            pass

    # 2. 배치 규격
    LINE_HEIGHT = 24
    START_Y = 118
    
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

    # 3. 덜컹거림 완벽 차단 키프레임 생성
    # 각 메시지당 2초 주기 (1.75초 정지, 0.25초 부드러운 전진 이동만 수행)
    step_duration = 2.0
    total_duration = total_items * step_duration
    
    keyframes_list = []
    for step in range(total_items):
        start_pct = (step / total_items) * 100
        hold_pct = ((step + 0.85) / total_items) * 100
        move_pct = ((step + 1.0) / total_items) * 100

        cur_y = -(step * LINE_HEIGHT)
        next_y = -((step + 1) * LINE_HEIGHT)

        # 현재 위치 유지 구간 (정지)
        keyframes_list.append(f"{start_pct:.2f}% {{ transform: translateY({cur_y}px); }}")
        keyframes_list.append(f"{hold_pct:.2f}% {{ transform: translateY({cur_y}px); }}")
        # 다음 위치로만 올라가는 단방향 전진
        keyframes_list.append(f"{move_pct:.2f}% {{ transform: translateY({next_y}px); }}")

    keyframes_css = "\n        ".join(keyframes_list)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="350" viewBox="0 0 800 350">
  <defs>
    <!-- 입력창(y=290)과 LIVE 배지(y=18~40)를 절대 침범하지 않도록 완벽 차단 -->
    <clipPath id="chat-view-area">
      <rect x="0" y="56" width="800" height="226" />
    </clipPath>
    <style>
      .chat-text {{
        font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', -apple-system, sans-serif;
        font-size: 13.5px;
      }}
      @keyframes liveStepScroll {{
        {keyframes_css}
      }}
      #chatScrollGroup {{
        /* linear로 주어야 키프레임 사이에서 위아래로 덜컹거리는 오버슈트가 완전히 사라집니다 */
        animation: liveStepScroll {total_duration}s linear infinite;
      }}
    </style>
  </defs>

  <!-- 1. 배경 -->
  {bg_tag}
  <rect width="800" height="350" fill="#000000" opacity="0.45"/>

  <!-- 2. 스크롤 채팅 영역 -->
  <g clip-path="url(#chat-view-area)">
    <g id="chatScrollGroup" transform="translate(38, 0)">
    {items_svg}
    </g>
  </g>

  <!-- 3. 상단 LIVE 배지 -->
  <g transform="translate(20, 18)">
    <rect width="46" height="22" rx="4" fill="#FF2D55"/>
    <text x="10" y="15" fill="#FFFFFF" font-family="'Malgun Gothic', sans-serif" font-weight="bold" font-size="11px">LIVE</text>
  </g>

  <!-- 4. 하단 입력창 UI -->
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
