from fastapi import FastAPI, Response
import os
import base64

app = FastAPI()

@app.get("/")
def get_live_overlay():
    # 배경 이미지(bg.png)를 오직 CSS 배경(background)으로만 안전하게 처리
    bg_style = "background-color: #0d0d0d;"
    if os.path.exists("bg.png"):
        try:
            with open("bg.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                bg_style = f"background-image: url('data:image/png;base64,{encoded_string}'); background-size: cover; background-position: center; background-repeat: no-repeat;"
        except:
            pass

    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Scon Live Chat</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            """ + bg_style + """
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            overflow: hidden;
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;
            height: 100vh;
        }
        .overlay-container {
            width: 420px;
            background: rgba(0, 0, 0, 0.75);
            box-sizing: border-box;
            padding: 15px;
            display: flex;
            flex-direction: column;
            position: relative;
            border-radius: 8px;
            margin: 20px;
        }
        .live-badge {
            display: inline-block;
            background-color: #FF2D55;
            color: white;
            font-weight: bold;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 4px;
            margin-bottom: 10px;
            width: fit-content;
        }
        .chat-scroll-box {
            height: 210px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 8px;
        }
        .chat-item {
            font-size: 13px;
            line-height: 1.4;
            animation: fadeInSlide 0.3s ease-out forwards;
            word-break: break-all;
        }
        @keyframes fadeInSlide {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .system-msg {
            color: #AAAAAA;
        }
        .username {
            font-weight: bold;
        }
        .message-text {
            color: #FFFFFF;
        }
        .input-box {
            margin-top: 12px;
            background: rgba(40, 40, 40, 0.9);
            border-radius: 16px;
            padding: 8px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .input-placeholder {
            color: #888888;
            font-size: 11px;
        }
        .heart {
            color: #FF5A78;
            font-weight: bold;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="overlay-container">
        <div class="live-badge">LIVE</div>
        <div class="chat-scroll-box" id="chatBox"></div>
        <div class="input-box">
            <span class="input-placeholder">채팅에 참여하세요...</span>
            <span class="heart">♥</span>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        
        const palette = ["#FF6E6E", "#6EE273", "#73BEFF", "#FFC850", "#DC82FF", "#50E6D2", "#FF9650"];
        function getColor(name) {
            let hash = 0;
            for (let i = 0; i < name.length; i++) {
                hash = name.charCodeAt(i) + ((hash << 5) - hash);
            }
            return palette[Math.abs(hash) % palette.length];
        }

        function appendChat(u, m) {
            const div = document.createElement('div');
            div.className = 'chat-item';

            if (u === "System") {
                div.innerHTML = '<span class="system-msg">System: ' + m + '</span>';
            } else {
                const color = getColor(u);
                div.innerHTML = '<span class="username" style="color: ' + color + ';">' + u + '</span><span class="message-text">: ' + m + '</span>';
            }

            chatBox.appendChild(div);

            if (chatBox.children.length > 7) {
                chatBox.removeChild(chatBox.children[0]);
            }
        }

        const samplePool = [
            ["System", "채팅에 참여해 스콘즈를 응원하세요!"],
            ["스콘팬1", "오늘 의상 진짜 미쳤다ㅠㅠㅠ"],
            ["김스콘", "실시간으로 보고 있는데 너무 떨려"],
            ["토끼단", "스콘즈 화이팅!! 언제나 응원해"],
            ["모찌", "노래 선곡 미쳤다 진짜"],
            ["별빛스콘", "댓글 읽어주세요 제발요ㅠㅠ"],
            ["체리", "오늘 라이브 레전드 찍네ㅋㅋㅋ"]
        ];

        let index = 0;
        for (let j = 0; j < 4; j++) {
            appendChat(samplePool[index][0], samplePool[index][1]);
            index = (index + 1) % samplePool.length;
        }

        setInterval(() => {
            appendChat(samplePool[index][0], samplePool[index][1]);
            index = (index + 1) % samplePool.length;
        }, 2500);
    </script>
</body>
</html>"""
    return Response(content=html_content, media_type="text/html")
