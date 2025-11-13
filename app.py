from flask import Flask, render_template_string, request, jsonify
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 이메일 설정
GMAIL_USER = "ksj6704@gmail.com"
GMAIL_PASS = "grxt gqpz dcss vydb"  # Gmail 앱 비밀번호

# HTML 페이지 (Flask가 직접 렌더링)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>이사 견적 요청서</title>
  <script src="//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js"></script>
  <style>
    body {
      font-family: 'Pretendard', sans-serif;
      max-width: 600px;
      margin: 50px auto;
      padding: 20px;
      background: #f7f8fa;
    }
    h1 {
      text-align: center;
      margin-bottom: 30px;
      color: #333;
    }
    form {
      background: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    label {
      font-weight: bold;
      display: block;
      margin-top: 15px;
    }
    input, textarea, select, button {
      width: 100%;
      padding: 10px;
      margin-top: 6px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 15px;
    }
    button {
      background: #0078ff;
      color: white;
      font-weight: bold;
      margin-top: 20px;
      cursor: pointer;
      transition: 0.3s;
    }
    button:hover {
      background: #005fcc;
    }
  </style>
</head>
<body>
  <h1>이사 견적 요청서</h1>
  <form id="estimateForm">
    <label>이름</label>
    <input type="text" name="name" required />

    <label>연락처</label>
    <input type="tel" name="phone" required placeholder="010-1234-5678" />

    <label>출발지 주소</label>
    <div style="display: flex; gap: 8px;">
      <input type="text" id="fromAddress" name="fromAddress" readonly required />
      <button type="button" onclick="searchAddress('fromAddress')">주소검색</button>
    </div>

    <label>도착지 주소</label>
    <div style="display: flex; gap: 8px;">
      <input type="text" id="toAddress" name="toAddress" readonly required />
      <button type="button" onclick="searchAddress('toAddress')">주소검색</button>
    </div>

    <label>이사 날짜</label>
    <input type="date" name="moveDate" required />

    <label>짐 종류 / 크기</label>
    <select name="truckSize" required>
      <option value="">선택해주세요</option>
      <option value="1톤 트럭">1톤 트럭</option>
      <option value="2.5톤 트럭">2.5톤 트럭</option>
      <option value="5톤 이상">5톤 이상</option>
    </select>

    <label>추가 요청사항</label>
    <textarea name="memo" rows="4" placeholder="예: 피아노 운반, 포장 이사 등"></textarea>

    <button type="submit">견적 요청하기</button>
  </form>

  <script>
    function searchAddress(targetId) {
      new daum.Postcode({
        oncomplete: function(data) {
          document.getElementById(targetId).value = data.address;
        }
      }).open();
    }

    document.getElementById("estimateForm").addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = Object.fromEntries(new FormData(e.target).entries());
      const response = await fetch("/send-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const result = await response.json();
      alert(result.message);
    });
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()
    if not data:
        return jsonify({"message": "⚠️ 전송 데이터가 없습니다."}), 400

    subject = f"이사 견적 요청 - {data.get('name')}"
    body = f"""
🔹 이름: {data.get('name')}
🔹 연락처: {data.get('phone')}
🔹 출발지: {data.get('fromAddress')}
🔹 도착지: {data.get('toAddress')}
🔹 이사 날짜: {data.get('moveDate')}
🔹 짐 종류 / 크기: {data.get('truckSize')}
🔹 추가 요청사항: {data.get('memo')}
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        return jsonify({"message": "✅ 견적 요청이 성공적으로 전송되었습니다!"})
    except Exception as e:
        print("메일 전송 실패:", e)
        return jsonify({"message": f"⚠️ 이메일 전송 중 오류 발생: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
