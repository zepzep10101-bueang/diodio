from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# 작가 10명 기본 데이터 초기화
initial_writers = {}
for i in range(1, 11):
    initial_writers[f"writer{i}"] = {
        "name": f"작가 {i}",
        "chars": 0,
        "memo": "오늘도 마감 파이팅!",
        "checked": False,
        "image": ""
    }

db: Dict[str, Any] = {
    "theme": "naver",
    "writers": initial_writers
}

class UpdateData(BaseModel):
    writer_id: str
    name: str
    chars: int
    memo: str
    checked: bool
    image: str

class ThemeUpdate(BaseModel):
    theme: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>기록은, TheMagam</title>
        <style>
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                margin: 0;
                padding: 30px;
                transition: background 0.3s, color 0.3s;
            }}
            /* 테마별 파스텔 색상 정의 */
            body.naver {{ background-color: #f1f8f5; color: #2d6a4f; }}
            body.naver .card {{ background-color: #e8f5e9; border: 1px solid #c8e6c9; }}
            body.naver button.save-btn {{ background-color: #2d6a4f; color: white; }}

            body.ridi {{ background-color: #f0f4f8; color: #1d3557; }}
            body.ridi .card {{ background-color: #e2eafc; border: 1px solid #d0ddec; }}
            body.ridi button.save-btn {{ background-color: #1d3557; color: white; }}

            body.kakao {{ background-color: #fffdf0; color: #7f5539; }}
            body.kakao .card {{ background-color: #fff3b0; border: 1px solid #ffe680; }}
            body.kakao button.save-btn {{ background-color: #b5838d; color: white; }}

            .header {{ text-align: center; margin-bottom: 30px; }}
            .theme-buttons button {{
                padding: 10px 20px;
                margin: 0 5px;
                border: none;
                border-radius: 20px;
                cursor: pointer;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .card {{
                border-radius: 15px;
                padding: 20px;
                width: 220px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .card input[type="text"], .card input[type="number"], .card textarea {{
                width: 100%;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 6px;
                box-sizing: border-box;
                font-size: 14px;
            }}
            .card label {{
                font-size: 13px;
                font-weight: bold;
            }}
            .preview-img {{
                width: 100%;
                height: 100px;
                object-fit: cover;
                border-radius: 8px;
                background: #fff;
                border: 1px dashed #ccc;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                color: #888;
            }}
            button.save-btn {{
                border: none;
                padding: 8px;
                width: 100%;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body class="{db['theme']}" id="body-tag">
        <div class="header">
            <h1>기록은, TheMagam 🌟</h1>
            <p>10명의 작가 실시간 마감 & 작업 공유 공간</p>
            <div class="theme-buttons">
                <button style="background:#e8f5e9; color:#2d6a4f;" onclick="setTheme('naver')">초록 (네이버)</button>
                <button style="background:#e2eafc; color:#1d3557;" onclick="setTheme('ridi')">파랑 (리디)</button>
                <button style="background:#fff3b0; color:#b5838d;" onclick="setTheme('kakao')">노랑 (카카오)</button>
            </div>
        </div>

        <div class="container" id="card-container"></div>

        <script>
            let currentTheme = "{db['theme']}";

            async function loadData() {{
                const res = await fetch('/data');
                const data = await res.json();
                
                // 테마 동기화 유지
                currentTheme = data.theme;
                document.getElementById('body-tag').className = currentTheme;
                
                const container = document.getElementById('card-container');
                container.innerHTML = '';
                
                for (const [id, info] of Object.entries(data.writers)) {{
                    let imgTag = info.image ? `<img src="${{info.image}}" class="preview-img">` : `<div class="preview-img">사진 없음</div>`;
                    
                    container.innerHTML += `
                        <div class="card">
                            <label>작가 이름</label>
                            <input type="text" value="${{info.name}}" id="name_${{id}}">
                            
                            <label>출석 체크 <input type="checkbox" ${{info.checked ? 'checked' : ''}} id="check_${{id}}"></label>
                            
                            <label>오늘 글자수</label>
                            <input type="number" value="${{info.chars}}" id="chars_${{id}}">
                            
                            <label>이미지 주소(URL)</label>
                            <input type="text" value="${{info.image}}" id="image_${{id}}" placeholder="이미지 링크 입력">
                            ${{imgTag}}
                            
                            <label>서브칸 메모</label>
                            <textarea id="memo_${{id}}" rows="2">${{info.memo}}</textarea>
                            
                            <button class="save-btn" onclick="saveData('${{id}}')">저장하기</button>
                        </div>
                    `;
                }}
            }}

            async function setTheme(themeName) {{
                await fetch('/theme', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ theme: themeName }})
                }});
                loadData();
            }}

            async function saveData(writerId) {{
                const name = document.getElementById(`name_${{writerId}}`).value;
                const checked = document.getElementById(`check_${{writerId}}`).checked;
                const chars = parseInt(document.getElementById(`chars_${{writerId}}`).value) || 0;
                const image = document.getElementById(`image_${{writerId}}`).value;
                const memo = document.getElementById(`memo_${{writerId}}`).value;

                await fetch('/update', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ writer_id: writerId, name, chars, memo, checked, image }})
                }});
                alert('저장되었습니다!');
                loadData();
            }}

            loadData();
            setInterval(loadData, 4000); // 4초마다 실시간 동기화
        </script>
    </body>
    </html>
    """

@app.get("/data")
def get_data():
    return db

@app.post("/theme")
def update_theme(data: ThemeUpdate):
    db["theme"] = data.theme
    return {"status": "success"}

@app.post("/update")
def update_writer(data: UpdateData):
    if data.writer_id in db["writers"]:
        db["writers"][data.writer_id].update({
            "name": data.name,
            "chars": data.chars,
            "memo": data.memo,
            "checked": data.checked,
            "image": data.image
        })
    return {"status": "success"}
