from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Dữ liệu mẫu cho lịch
    schedule = {
        "title": "Lịch đăng ký sân bóng DUE",
        "month": "Tháng 3",
        "days": [
            {"day": "Thứ 2", "date": 10, "times": ["17:00", "18:00", "19:00", "20:00"]},
            {"day": "Thứ 3", "date": 11, "times": ["17:00", "18:00", "19:00", "20:00"]},
            {"day": "Thứ 4", "date": 12, "times": ["17:00", "18:00", "19:00", "20:00"]},
            {"day": "Thứ 5", "date": 13, "times": ["17:00", "18:00", "19:00", "20:00"]},
            {"day": "Thứ 6", "date": 14, "times": ["17:00", "18:00", "19:00", "20:00"]},
            {"day": "Thứ 7", "date": 15, "times": ["17:00", "18:00", "19:00", "20:00"]},
            {"day": "Chủ nhật", "date": 16, "times": ["17:00", "18:00", "19:00", "20:00"]}
        ],
        "booked_dates": [
            {"date": "13/03/2025", "time": "18:00"},
            {"date": "14/03/2025", "time": "18:00"}
        ]
    }
    return render_template('index.html', schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True)