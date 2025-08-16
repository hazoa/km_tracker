import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import zoneinfo
import pandas as pd

st.set_page_config(page_title="KM-Tracker", page_icon="🚗")

# ---- Google Sheets Setup (CLOUD) ----
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)  # FIX
gc = gspread.authorize(creds)

SPREADSHEET_KEY = st.secrets["SPREADSHEET_KEY"]  # FIX: Secret-Name, nicht der Key-Wert
WORKSHEET = "trips"

# Spreadsheet + Worksheet öffnen
sh = gc.open_by_key(SPREADSHEET_KEY)
try:
    ws = sh.worksheet(WORKSHEET)
except gspread.WorksheetNotFound:
    st.error(f"Worksheet '{WORKSHEET}' nicht gefunden – Tab unten bitte exakt so benennen.")
    st.stop()

# ---- Daten laden ----
df = pd.DataFrame(ws.get_all_records())
last_odo = float(pd.to_numeric(df["odometer_km"], errors="coerce").iloc[0]) if not df.empty else None

# ---- UI ----
st.title("🚗 Kilometer-Tracker")
odo = st.number_input("Aktueller Kilometerstand", min_value=0.0, step=0.1,
                      value=last_odo if last_odo is not None else 0.0, format="%.1f")
comment = st.text_input("Kommentar (optional)", "")

trip_preview = round(odo - last_odo, 1) if last_odo is not None and odo >= last_odo else None
if trip_preview is not None:
    st.info(f"Trip seit letztem Eintrag: {trip_preview} km")

# ---- Speichern ----
if st.button("Speichern", use_container_width=True):
    ts = datetime.now(zoneinfo.ZoneInfo("Europe/Berlin")).isoformat(timespec="seconds")  # mit TZ
    ws.insert_row([ts, odo, trip_preview, comment], index=2)
    st.success("Gespeichert! Seite neu laden für aktualisierte Ansicht.")

st.divider()

# ---- Anzeige & Export ----
df = pd.DataFrame(ws.get_all_records())
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Als CSV herunterladen", csv, "km_trips.csv", "text/csv", use_container_width=True)
