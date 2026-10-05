from fastapi import FastAPI, Response
import urllib.parse
import os
import base64
import json

app = FastAPI()

@app.get("/")
def get_live_overlay(users: str = None, msgs: str = None):
    if not users or not msgs:
        user_list = []
        msg_list = []
    else:
        user_list = [urllib.parse.unquote(u).strip() for u in users.split(",") if u.strip()]
        msg_list = [urllib.parse.unquote(m).strip() for m in msgs.split(",") if m.strip()]

    # 1. 배경 이미지 (bg.png)
    bg_tag = '<rect width="800" height="350" fill="#141414"/>'
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_tag = f'<image x="0" y="0" width="800" height="350" href="data:image/png;base64,{encoded_string}" preserveAspectRatio="none"/>'
        except Exception:
            pass

    js_users = json.dumps(user_list)
    js_msgs = json.dumps(msg_list)

    # 원본 사이트 개발자 도구와 100% 동일한 순수 SVG 구조
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
    </style>
  </defs>

  <!-- 1. 배경 -->
  {bg_tag}
  <!-- 배경 어둡게 -->
  <rect width="800" height="350" fill="#000000" opacity="0.45"/>

  <!-- 2. 스크롤 채팅 영역 (JS가 이 그룹 내부에 text 노드를 실시간 생성) -->
  <g clip-path="url(#chat-view-area)">
    <g id="chatScrollGroup" transform="translate(20, 0)">
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

  <script type="text/javascript">
    <![CDATA[
    (function() {{
      const inputUsers = {js_users};
      const inputMsgs = {js_msgs};

      const samplePool = [
        ["System", "채팅에 참여해 스콘즈를 응원하세요!"],
        ["스콘팬1", "오늘 의상 진짜 미쳤다ㅠㅠㅠ"],
        ["김스콘", "실시간으로 보고 있는데 너무 떨려"],
        ["토끼단", "스콘즈 화이팅!! 언제나 응원해"],
        ["모찌", "노래 선곡 미쳤다 진짜"],
        ["별빛스콘", "댓글 읽어주세요 제발요ㅠㅠ"],
        ["체리", "오늘 라이브 레전드 찍네ㅋㅋㅋ"]
      ];

      const activeUsers = inputUsers.length > 0 ? inputUsers : samplePool.map(i => i[0]);
      const activeMsgs = inputMsgs.length > 0 ? inputMsgs : samplePool.map(i => i[1]);

      const palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"];
      function getColor(name) {{
        let hash = 0;
        for (let i = 0; i < name.length; i++) {{
          hash = name.charCodeAt(i) + ((hash << 5) - hash);
        }}
        return palette[Math.abs(hash) % palette.length];
      }}

      const chatGroup = document.getElementById("chatScrollGroup");
      let chatHistory = [];
      const MAX_LINES = 7;
      const START_Y = 85;
      const LINE_HEIGHT = 28;

      function render() {{
        while (chatGroup.firstChild) {{
          chatGroup.removeChild(chatGroup.firstChild);
        }}

        chatHistory.forEach((item, idx) => {{
          const yPos = START_Y + (idx * LINE_HEIGHT);
          const textEl = document.createElementNS("http://www.w3.org/2000/svg", "text");
          textEl.setAttribute("x", "0");
          textEl.setAttribute("y", yPos);
          textEl.setAttribute("class", "chat-text");

          if (item.u === "System") {{
            textEl.setAttribute("fill", "#AAAAAA");
            textEl.textContent = "System: " + item.m;
          }} else {{
            const userSpan = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
            userSpan.setAttribute("fill", getColor(item.u));
            userSpan.setAttribute("font-weight", "bold");
            userSpan.textContent = item.u;

            const msgSpan = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
            msgSpan.setAttribute("fill", "#FFFFFF");
            msgSpan.textContent = ": " + item.m;

            textEl.appendChild(userSpan);
            textEl.appendChild(msgSpan);
          }}
          chatGroup.appendChild(textEl);
        }});
      }}

      function pushChat(u, m) {{
        chatHistory.push({{ u, m }});
        if (chatHistory.length > MAX_LINES) {{
          chatHistory.shift();
        }}
        render();
      }}

      let curIdx = 0;
      const initCount = Math.min(4, activeUsers.length);
      for (let j = 0; j < initCount; j++) {{
        pushChat(activeUsers[curIdx], activeMsgs[curIdx]);
        curIdx = (curIdx + 1) % activeUsers.length;
      }}

      setInterval(() => {{
        pushChat(activeUsers[curIdx], activeMsgs[curIdx]);
        curIdx = (curIdx + 1) % activeUsers.length;
      }}, 2500);
    }})();
    ]]>
  </script>
</svg>'''

    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )
