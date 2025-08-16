import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd



st.set_page_config(page_title="KM-Tracker", page_icon="🚗")

# ---- Google Sheets Setup ----
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service.json", scopes=SCOPES)
gc = gspread.authorize(creds)

SPREADSHEET_KEY = "1Lhjc0A_DwrEOM-_iBUr7X-0Ryd9Q897uG9RKP0cdh5I"   # dein Spreadsheet-Key
SHEET_NAME = "KM_Tracker"   # dein Spreadsheet-Name
WORKSHEET = "trips"         # Tabellenblatt-Name
sh = gc.open_by_key(SPREADSHEET_KEY)
ws = sh.worksheet(WORKSHEET)

# Worksheet sicher holen
try:
    ws = sh.worksheet("trips")
except gspread.WorksheetNotFound:
    st.error("Worksheet 'trips' nicht gefunden – bitte Tab unten exakt 'trips' nennen.")
    st.stop()

# ---- Daten laden ----

df_all = pd.DataFrame(ws.get_all_records())
last_odo = float(pd.to_numeric(df_all["odometer_km"], errors="coerce").iloc[0]) if not df_all.empty else None

# ---- UI ----
st.title("🚗 Kilometer-Tracker")

rows = ws.get_all_records()
last_odo = float(rows[0]["odometer_km"]) if rows else None

odo = st.number_input("Aktueller Kilometerstand", min_value=0.0, step=0.1,
                      value=last_odo if last_odo else 0.0, format="%.1f")
comment = st.text_input("Kommentar (optional)", "")

trip_preview = round(odo - last_odo, 1) if last_odo is not None and odo >= last_odo else None
if trip_preview is not None:
    st.info(f"Trip seit letztem Eintrag: {trip_preview} km")

if st.button("Speichern", use_container_width=True):
    ts = datetime.now().isoformat(timespec="seconds")
    ws.insert_row([ts, odo, trip_preview, comment], index=2)  # unter Header
    st.success("Gespeichert! Seite neu laden für Ansicht.")

st.divider()
df = pd.DataFrame(ws.get_all_records())
st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Als CSV herunterladen", csv, "km_trips.csv", "text/csv")
