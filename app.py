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
        ("Protégez votre partenaire et faites un auto-test VIH","Connaître votre statut VIH vous aide à vous protéger et à protéger votre partenaire. Si vous avez changé de partenaire ou avez un doute, faites un auto-test VIH dès aujourd’hui."),
        ("Confirmez tout résultat réactif après une exposition possible en faisant un auto-test VIH","Après un rapport non protégé, une rupture de préservatif ou un partage de matériel d’injection, utilisez un auto-test VIH rapidement et confirmez tout résultat positif dans un centre de santé."),
        ("Préparez votre renouvellement trimestriel de PrEP avec un auto-test VIH","Avant de renouveler votre PrEP, faites un auto-test VIH. Tester tous les 3 mois vous aide à rester protégé et en bonne santé."),
        ("Renforcez votre confiance pour maintenir ou reprendre la PrEP/PEP avec un auto-test VIH","Si vous avez interrompu la PrEP ou avez besoin d’une PEP, commencez par un auto-test VIH. Connaître votre statut vous permet d’agir rapidement et en toute sécurité."),
        ("Prenez le contrôle grâce à une détection précoce avec un auto-test VIH","Un dépistage précoce signifie de meilleurs résultats de santé. Utilisez un auto-test VIH régulièrement, surtout si vous avez un risque continu."),
        ("Utilisez l’auto-test VIH comme partie intégrante de vos soins personnalisés après une pause de PrEP","Si vous avez fait une pause dans la PrEP et envisagez de la reprendre, faites un auto-test VIH pour confirmer votre statut avant de redémarrer."), 
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



