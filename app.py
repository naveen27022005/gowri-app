from datetime import datetime, timedelta
import requests
import gradio as gr
from geopy.geocoders import Nominatim

# -------------------------------------------------
# 📍 Get Coordinates
# -------------------------------------------------
def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="gowri_app")
    location = geolocator.geocode(city_name)

    if location:
        return location.latitude, location.longitude
    return None, None

# -------------------------------------------------
# 🌅 Sunrise / Sunset API
# -------------------------------------------------
def get_sun_times(lat, lon, date):
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&date={date}&formatted=0"
    response = requests.get(url).json()

    sunrise = datetime.fromisoformat(response["results"]["sunrise"])
    sunset = datetime.fromisoformat(response["results"]["sunset"])

    return sunrise, sunset

# -------------------------------------------------
# 🪐 Hora Planet Cycle
# -------------------------------------------------
HORA_CYCLE = [
    "🪐 Saturn",
    "♃ Jupiter",
    "♂ Mars",
    "☀ Sun",
    "♀ Venus",
    "☿ Mercury",
    "☽ Moon"
]

DAY_START_PLANET = {
    0: "☽ Moon",
    1: "♂ Mars",
    2: "☿ Mercury",
    3: "♃ Jupiter",
    4: "♀ Venus",
    5: "🪐 Saturn",
    6: "☀ Sun"
}

# -------------------------------------------------
# 🕒 Formatter
# -------------------------------------------------
def fmt(t):
    return t.strftime("%H:%M:%S")

# -------------------------------------------------
# 🔮 Main Logic
# -------------------------------------------------
def predict(city_name, date_str):
    try:
        lat, lon = get_coordinates(city_name)
        if lat is None:
            return "❌ Invalid city"

        sunrise_utc, sunset_utc = get_sun_times(lat, lon, date_str)

        ist = timedelta(hours=5, minutes=30)
        sunrise = sunrise_utc + ist
        sunset = sunset_utc + ist

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = date_obj.weekday()

        start_planet = DAY_START_PLANET[weekday]
        start_idx = HORA_CYCLE.index(start_planet)

        result = []
        result.append(f"📅 {date_str} ({date_obj.strftime('%A')})")
        result.append(f"🌅 Sunrise: {fmt(sunrise)}")
        result.append(f"🌇 Sunset: {fmt(sunset)}")
        result.append(f"🪐 Starting Planet: {start_planet}\n")

        def block(start, end, parts, idx, label):
            dur = (end - start).total_seconds() / parts
            td = timedelta(seconds=dur)
            cur = start

            lines = [f"{label}"]
            for i in range(parts):
                nxt = cur + td
                planet = HORA_CYCLE[(idx+i)%7]

                lines.append(
                    f"{i+1:02d} | {fmt(cur)} → {fmt(nxt)} | {planet}"
                )
                cur = nxt

            return "\n".join(lines)

        # Day
        result.append(block(sunrise, sunset, 8, start_idx, "🌞 DAY GOWRI"))

        # Night
        next_day = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        sunrise_next,_ = get_sun_times(lat, lon, next_day)
        sunrise_next += ist

        result.append("")
        result.append(block(sunset, sunrise_next, 8, (start_idx+8)%7, "🌙 NIGHT GOWRI"))

        return "\n".join(result)

    except Exception as e:
        return str(e)

# -------------------------------------------------
# 🎨 Gradio UI
# -------------------------------------------------
def ui(city, date):
    return f"<pre>{predict(city,date)}</pre>"

with gr.Blocks() as demo:
    gr.Markdown("# 🌞 Gowri Panchangam Calculator")

    city = gr.Textbox(label="City", placeholder="Chennai")
    date = gr.Textbox(label="Date YYYY-MM-DD")

    out = gr.HTML()

    gr.Button("Calculate").click(ui,[city,date],out)

demo.launch(share = True)

