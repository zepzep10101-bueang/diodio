from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any
import shutil
import os

app = FastAPI()

# 업로드된 이미지를 저장할 폴더 생성
UPLOAD_DIR = "static_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    "writers": initial_writers
}

@app.get("/", response_class=HTMLResponse)
def read_root():
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>작가 대통합⭐</title>
        <style>
            :root {{
                --bg-color: #f7f9f6; /* 눈이 가장 편안한 은은한 파스텔톤 배경 */
                --card-naver: #e8f5e9;
                --card-ridi: #e2eafc;
                --card-kakao: #fff3b0;
                --text-color: #2f3e46;
            }}
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 30px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                font-size: 28px;
                color: #354f52;
            }}
            .container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
                max-width: 1200px;
                margin: 0 auto;
            }}
            /* 카드 기본 스타일 (네이버 초록 테마 기본) */
            .card {{
                background-color: var(--card-naver);
                border-radius: 15px;
                padding: 20px;
                width: 220px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                display: flex;
                flex-direction: column;
                gap: 8px;
                transition: background 0.3s;
            }}
            .card input[type="text"], .card input[type="number"], .card textarea, .card select {{
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
                height: 90px;
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
                background-color: #52796f;
                color: white;
                border: none;
                padding: 8px;
                width: 100%;
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 5px;
            }}
            button.save-btn:hover {{
                background-color: #354f52;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>작가 대통합⭐</h1>
            <p>우리들의 편안한 실시간 마감 & 작업 공간</p>
        </div>

        <div class="container" id="card-container"></div>

        <script>
            async function loadData() {{
                const res = await fetch('/data');
                const data = await res.json();
                
                const container = document.getElementById('card-container');
                container.innerHTML = '';
                
                for (const [id, info] of Object.entries(data.writers)) {{
                    let imgTag = info.image ? `<img src="${{info.image}}" class="preview-img">` : `<div class="preview-img">사진 없음</div>`;
                    
                    // 각자 자기 칸에서만 테마를 고를 수 있는 셀렉트 박스 상태 유지
                    let selectedTheme = localStorage.getItem(`theme_${{id}}`) || 'naver';
                    
                    container.innerHTML += `
                        <div class="card" id="card_box_${{id}}" style="background-color: ${{getThemeColor(selectedTheme)}};">
                            <label>테마 선택</label>
                            <select onchange="changeCardTheme('${{id}}', this.value)">
                                <option value="naver" ${{selectedTheme === 'naver' ? 'selected' : ''}}>초록 (네이버)</option>
                                <option value="ridi" ${{selectedTheme === 'ridi' ? 'selected' : ''}}>파랑 (리디)</option>
                                <option value="kakao" ${{selectedTheme === 'kakao' ? 'selected' : ''}}>노랑 (카카오)</option>
                            </select>

                            <label>작가 이름</label>
                            <input type="text" value="${{info.name}}" id="name_${{id}}">
                            
                            <label>출석 체크 <input type="checkbox" ${{info.checked ? 'checked' : ''}} id="check_${{id}}"></label>
                            
                            <label>오늘 글자수</label>
                            <input type="number" value="${{info.chars}}" id="chars_${{id}}">
                            
                            <label>내 컴퓨터 사진 올리기</label>
                            <input type="file" id="file_${{id}}" accept="image/*" style="font-size:11px;">
                            ${{imgTag}}
                            
                            <label>서브칸 메모</label>
                            <textarea id="memo_${{id}}" rows="2">${{info.memo}}</textarea>
                            
                            <button class="save-btn" onclick="saveData('${{id}}')">저장하기</button>
                        </div>
                    `;
                }}
            }}

            function getThemeColor(theme) {{
                if (theme === 'naver') return '#e8f5e9';
                if (theme === 'ridi') return '#e2eafc';
                if (theme === 'kakao') return '#fff3b0';
                return '#e8f5e9';
            }}

            function changeCardTheme(writerId, theme) {{
                localStorage.setItem(`theme_${{writerId}}`, theme);
                document.getElementById(`card_box_${{writerId}}`).style.backgroundColor = getThemeColor(theme);
            }}

            async function saveData(writerId) {{
                const name = document.getElementById(`name_${{writerId}}`).value;
                const checked = document.getElementById(`check_${{writerId}}`).checked;
                const chars = parseInt(document.getElementById(`chars_${{writerId}}`).value) || 0;
                const memo = document.getElementById(`memo_${{writerId}}`).value;
                const fileInput = document.getElementById(`file_${{writerId}}`);

                const formData = new FormData();
                formData.append("writer_id", writerId);
                formData.append("name", name);
                formData.append("chars", chars);
                formData.append("memo", memo);
                formData.append("checked", checked);
                
                if (fileInput.files.length > 0) {{
                    formData.append("file", fileInput.files[0]);
                }}

                const res = await fetch('/update', {{
                    method: 'POST',
                    body: formData
                }});
                
                if (res.ok) {{
                    alert('저장되었습니다!');
                    loadData();
                }} else {{
                    alert('저장 실패 ㅠㅠ 다시 시도해줘!');
                }}
            }}

            loadData();
            setInterval(loadData, 5000);
        </script>
    </body>
    </html>
    """

@app.get("/data")
def get_data():
    return db

@app.post("/update")
async def update_writer(
    writer_id: str = Form(...),
    name: str = Form(...),
    chars: int = Form(...),
    memo: str = Form(...),
    checked: bool = Form(...),
    file: UploadFile = File(None)
):
    if writer_id in db["writers"]:
        image_path = db["writers"][writer_id]["image"]
        
        # 파일이 새로 업로드되었다면 서버 폴더에 저장
        if file and file.filename:
            file_location = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_location, "wb+") as buffer:
                shutil.copyfileobj(file.file, buffer)
            image_path = f"/{file_location}"

        db["writers"][writer_id].update({
            "name": name,
            "chars": chars,
            "memo": memo,
            "checked": checked,
            "image": image_path
        })
    return {"status": "success"}
