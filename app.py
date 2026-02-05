from flask import Flask, request, Response
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

def ics_escape(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )

def yyyymmdd_utc(dt):
    return dt.strftime("%Y%m%d")

def dtstamp_utc(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")

@app.route("/invite.ics")
def invite():
    now = datetime.utcnow()

    start_date = yyyymmdd_utc(now)
    end_date = yyyymmdd_utc(now + timedelta(days=1))

    title = "Pick up your HIVST"
    event_description = "Please go to your local medical centre"

    # Alert 1: day before (either midnight or 9am the day before)
    alarm = request.args.get("alarm", "1day").lower()
    if alarm in ("9am", "same"):
        # 9am the day before (relative to 00:00 on event day)
        trigger_1 = "-PT15H"
        trigger_1_line = f"TRIGGER;RELATED=START:{trigger_1}"
    else:
        # midnight the day before
        trigger_1_line = "TRIGGER;RELATED=START:-P1D"

    # Alert 2: on the day of the event at 9am local time
    trigger_2_line = "TRIGGER;RELATED=START:PT9H"

    uid = f"{uuid.uuid4()}@ics-generator"

    ics = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Dynamic ICS Generator//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp_utc(now)}",
        f"DTSTART;VALUE=DATE:{start_date}",
        f"DTEND;VALUE=DATE:{end_date}",
        "RRULE:FREQ=MONTHLY;INTERVAL=6",
        f"SUMMARY:{ics_escape(title)}",
        f"DESCRIPTION:{ics_escape(event_description)}",

        # Alert 1 (day before)
        "BEGIN:VALARM",
        trigger_1_line,
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "END:VALARM",

        # Alert 2 (day of)
        "BEGIN:VALARM",
        trigger_2_line,
        "ACTION:DISPLAY",
        "DESCRIPTION:Reminder",
        "END:VALARM",

        "END:VEVENT",
        "END:VCALENDAR",
    ])

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



