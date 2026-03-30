from flask import Flask, Response
from datetime import datetime, timedelta, date
import uuid
import calendar

app = Flask(__name__)

def ics_escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )

def dtstamp_utc(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")

def yyyymmdd(d: date):
    return d.strftime("%Y%m%d")

def add_months(d: date, months: int) -> date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)

@app.route("/invite.ics")
def invite():
    now = datetime.utcnow()
    base_date = now.date()  # dynamic start = download date (UTC)

    # 6 different events (each repeats every 6 months; together = monthly forever)
    events_data = [
     ("ปกป้องตัวคุณและคู่ของคุณด้วยการตรวจเอชไอวีด้วยตนเอง","กำลังเริ่มคบคนใหม่หรือไม่แน่ใจสถานะเอชไอวีของคู่ของคุณ? การตรวจด้วยตนเองช่วยให้คุณมั่นใจและปกป้องสิ่งที่สำคัญ การตรวจเป็นประจำช่วยให้คุณควบคุมสุขภาพของตนเองและสนับสนุนการป้องกัน"),
("ยืนยันสถานะเอชไอวีของคุณหลังจากมีความเสี่ยง: ใช้ชุดตรวจเอชไอวีด้วยตนเองทันที","มีเพศสัมพันธ์โดยไม่ป้องกันหรือถุงยางแตกหรือไม่? ให้ตรวจเอชไอวีด้วยตนเองโดยเร็วที่สุด หากเหตุการณ์เกิดขึ้นภายใน 72 ชั่วโมง ให้รีบรับ PEP ทันที การดำเนินการอย่างรวดเร็วช่วยให้คุณปลอดภัยและได้รับข้อมูลที่ถูกต้อง"),
("เตรียมตัวสำหรับการรับ PrEP ครั้งถัดไปทุก 3 เดือนด้วยการตรวจเอชไอวีด้วยตนเอง","กำลังใช้ PrEP หรือไม่? หากคุณใช้ PrEP แบบรับประทานทุกวัน ควรตรวจเอชไอวีอย่างน้อยทุก 3 เดือน การตรวจอย่างสม่ำเสมอช่วยให้การใช้ PrEP ปลอดภัย มีประสิทธิภาพ และเป็นไปตามแผน"),
("เพิ่มความมั่นใจระหว่างการใช้หรือก่อนเริ่มใช้ PrEP อีกครั้งด้วยการตรวจเอชไอวีด้วยตนเอง","หยุดใช้ PrEP หรือกำลังคิดจะเริ่มใหม่หรือไม่? ก่อนเริ่มอีกครั้ง ควรยืนยันว่าคุณยังมีสถานะลบด้วยการตรวจด้วยตนเอง การตรวจเป็นประจำช่วยปกป้องคุณและทำให้แผนการป้องกันของคุณมีประสิทธิภาพ"),
("ควบคุมสุขภาพของคุณด้วยการตรวจเอชไอวีด้วยตนเองตั้งแต่เนิ่น ๆ","การรู้สึกสุขภาพดีไม่ได้หมายความว่าไม่มีเอชไอวี หลายคนไม่มีอาการในระยะแรก การตรวจด้วยตนเองช่วยให้คุณมีความชัดเจน ความมั่นใจ และควบคุมสถานะของตนเองได้"),
("ทำให้การตรวจเอชไอวีด้วยตนเองเป็นส่วนหนึ่งของการดูแลสุขภาพเฉพาะบุคคลหลังจากหยุดใช้ PrEP","จำไม่ได้ว่าครั้งสุดท้ายที่ตรวจเมื่อไหร่หรือไม่? ตอนนี้เป็นเวลาที่ดีในการตรวจด้วยตนเอง การตรวจอย่างสม่ำเสมอช่วยให้ตรวจพบได้เร็วและช่วยให้คุณมั่นใจในเส้นทางการป้องกันของคุณ")
]

    # Alerts:
    # - Day before: midnight the day before (relative to all-day start at 00:00)
    alarm_day_before = "TRIGGER;RELATED=START:-P1D"
    # - Day of: 9am local time on the day (00:00 + 9 hours)
    alarm_day_of = "TRIGGER;RELATED=START:PT9H"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dynamic ICS Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for i, (title, description) in enumerate(events_data):
        start_date = add_months(base_date, i)
        end_date = start_date + timedelta(days=1)

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@ics-generator",
            f"DTSTAMP:{dtstamp_utc(now)}",
            f"DTSTART;VALUE=DATE:{yyyymmdd(start_date)}",
            f"DTEND;VALUE=DATE:{yyyymmdd(end_date)}",
            "RRULE:FREQ=MONTHLY;INTERVAL=6",
            f"SUMMARY:{ics_escape(title)}",
            f"DESCRIPTION:{ics_escape(description)}",

            # Alert 1: day before
            "BEGIN:VALARM",
            alarm_day_before,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            # Alert 2: day of (9am)
            "BEGIN:VALARM",
            alarm_day_of,
            "ACTION:DISPLAY",
            "DESCRIPTION:Reminder",
            "END:VALARM",

            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")

    ics = "\r\n".join(lines) + "\r\n"

    return Response(
        ics,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=invite.ics"},
    )

@app.route("/")
def health():
    return "OK. Try /invite.ics"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)



