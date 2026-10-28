import asyncio
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import streamlit as st
from fastapi import HTTPException
from streamlit.errors import StreamlitSecretNotFoundError

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def load_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        value = None
    return str(value or os.environ.get(name, default))


for setting in ("GEMINI_API_KEY", "GEMINI_MODEL"):
    value = load_secret(setting, "gemini-2.5-flash" if setting == "GEMINI_MODEL" else "")
    if value:
        os.environ[setting] = value

from app.schemas import ItineraryResponse, TripRequest
from app.services import generate_itinerary


st.set_page_config(page_title="Wayfarer — Travel Planner", page_icon="✈️", layout="wide")
st.title("✈️ Wayfarer")
st.caption("Create a personalized travel itinerary with Google Gemini.")

with st.form("trip_preferences"):
    destination = st.text_input("Where do you want to go?", placeholder="e.g. Kyoto, Japan")
    budget = st.selectbox("Budget", ["Budget", "Moderate", "Luxury"], index=1)
    travel_style = st.selectbox("Travel style", ["Solo", "Couple", "Family", "Friends"], index=1)
    group_size = st.number_input("Group size", min_value=1, max_value=20, value=2)
    start_date = st.date_input("Start date", value=date.today() + timedelta(days=14))
    end_date = st.date_input("End date", value=date.today() + timedelta(days=20))
    interests = st.multiselect(
        "What are you interested in?",
        ["Food & drink", "Culture", "Nature", "Architecture", "Adventure", "Shopping"],
        default=["Food & drink", "Culture"],
    )
    submitted = st.form_submit_button("Create my itinerary", type="primary")

if submitted:
    try:
        trip = TripRequest(
            destination=destination,
            budget=budget,
            start_date=start_date,
            end_date=end_date,
            travel_style=travel_style,
            group_size=group_size,
            interests=interests,
        )
    except ValueError as exc:
        st.error(str(exc))
    else:
        if not load_secret("GEMINI_API_KEY"):
            st.error("Add GEMINI_API_KEY to Streamlit app secrets before generating an itinerary.")
        else:
            try:
                with st.spinner("Planning your trip..."):
                    result = asyncio.run(generate_itinerary(trip))
                if not isinstance(result, ItineraryResponse):
                    st.error("The itinerary service returned an unexpected response.")
                else:
                    st.session_state["itinerary"] = result.model_dump(mode="json")
                    st.session_state["destination"] = trip.destination
            except HTTPException as exc:
                st.error(str(exc.detail))
            except (RuntimeError, ValueError) as exc:
                st.error(f"Could not create the itinerary: {exc}")

itinerary_data = st.session_state.get("itinerary")
if itinerary_data:
    itinerary = ItineraryResponse.model_validate(itinerary_data)
    st.divider()
    st.subheader(f"Your trip to {st.session_state['destination']}")
    st.write(itinerary.trip_summary)
    st.metric("Estimated total cost", itinerary.total_estimated_cost)

    for day in itinerary.itinerary:
        date_label = day.date.strftime("%A, %B %d, %Y")
        with st.expander(f"Day {day.day} · {date_label}", expanded=day.day == 1):
            for activity in day.activities:
                st.markdown(f"**{activity.time_slot} · {activity.title}**")
                st.write(activity.description)
                st.caption(
                    f"{activity.category} · {activity.location} · "
                    f"Estimated cost: {activity.estimated_cost}"
                )

    st.download_button(
        "Download itinerary (JSON)",
        data=json.dumps(itinerary_data, indent=2, ensure_ascii=False),
        file_name="wayfarer-itinerary.json",
        mime="application/json",
    )

st.caption(
    "Prices and opening hours are estimates. This app does not book travel or save trips "
    "to a cloud account; download your itinerary to keep a copy."
)
