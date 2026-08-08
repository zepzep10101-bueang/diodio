from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# 임시 메모리 저장소 (작가별 데이터 및 테마 관리)
db: Dict[str, Any] = {
    "theme": "naver",  # 기본 테마: naver (초록), ridi (파랑), kakao (노랑)
    "writers": {
        "writer1": {"name": "작가 1", "chars": 4120, "memo": "작가 대통합☆", "checked": True},
        "writer2": {"name": "작가 2", "chars": 2500, "memo": "하루 1빡!", "checked": False},
        "writer3": {"name": "작가 3", "chars": 3100, "memo": "일해라! 일을 해야 돈이 들어오나니!", "checked": True},
    }
}

class UpdateData(BaseModel):
    writer_id: str
    chars: int
    memo: str
    checked: bool

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
            :root {{ --bg-color: #f1f8f5; --main-color: #2d6a4f; --card-bg: #e8f5e9; }}
            body.naver {{ --bg-color: #f1f8f5; --main-color: #2d6a4f; --card-bg: #e8f5e9; }}
            body.ridi {{ --bg-color: #f0f4f8; --main-color: #1d3557; --card-bg: #e2eafc; }}
            body.kakao {{ --bg-color: #fffdf0; --main-color: #b5838d; --card-bg: #fff3b0; }}
            body {{ font-family: 'Malgun Gothic', sans-serif; background-color: var(--bg-color); padding: 20px; transition: background 0.3s; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .container {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }}
            .card {{ background: var(--card-bg); border-radius: 12px; padding: 20px; width: 250px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            button.save-btn {{ background-color: var(--main-color); color: white; border: none; padding: 8px; width: 100%; border-radius: 6px; cursor: pointer; }}
            input, textarea {{ width: 100%; margin-bottom: 10px; padding: 8px; border: 1px solid #ccc; border-radius: 6px; }}
        </style>
    </head>
    <body class="{db['theme']}">
        <div class="header">
            <h1>기록은, TheMagam</h1>
            <div class="theme-buttons">
                <button onclick="setTheme('naver')">초록</button>
                <button onclick="setTheme('ridi')">파랑</button>
                <button onclick="setTheme('kakao')">노랑</button>
            </div>
        </div>
        <div class="container" id="card-container"></div>
        <script>
            async function loadData() {{
                const res = await fetch('/data');
                const data = await res.json();
                document.body.className = data.theme;
                const container = document.getElementById('card-container');
                container.innerHTML = '';
                for (const [id, info] of Object.entries(data.writers)) {{
                    container.innerHTML += `
                        <div class="card">
                            <h3>${{info.name}}</h3>
                            <label>출석 <input type="checkbox" ${{info.checked ? 'checked' : ''}} id="check_${{id}}"></label>
                            <input type="number" value="${{info.chars}}" id="chars_${{id}}">
                            <textarea id="memo_${{id}}">${{info.memo}}</textarea>
                            <button class="save-btn" onclick="saveData('${{id}}')">저장</button>
                        </div>`;
                }}
            }}
            async function setTheme(theme) {{ await fetch('/theme', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{theme}}) }}); loadData(); }}
            async function saveData(id) {{
                await fetch('/update', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, 
                body:JSON.stringify({{ writer_id:id, chars:parseInt(document.getElementById('chars_'+id).value), memo:document.getElementById('memo_'+id).value, checked:document.getElementById('check_'+id).checked }}) }});
                alert('저장!'); loadData();
            }}
            loadData(); setInterval(loadData, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/data")
def get_data(): return db

@app.post("/theme")
def update_theme(data: ThemeUpdate): db["theme"] = data.theme; return {"status": "success"}

@app.post("/update")
def update_writer(data: UpdateData):
    if data.writer_id in db["writers"]:
        db["writers"][data.writer_id].update({"chars": data.chars, "memo": data.memo, "checked": data.checked})
    return {"status": "success"}