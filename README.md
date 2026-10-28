# Wayfarer

**AI-powered travel itineraries, tailored to your dates, budget, group, and interests.**

Wayfarer is a travel-planning app built with Streamlit and Google Gemini. Enter your trip preferences to generate a day-by-day itinerary, review estimated costs, and download the result as JSON.

> **Scope:** The Streamlit edition is intentionally lightweight. It does not require Supabase, user accounts, or a separate backend deployment. It does not store trips in the cloud. The original React and FastAPI application remains in this repository.

## Features

- Personalized itineraries for trips of up to 31 days
- Budget, travel style, group size, dates, and interest preferences
- Day-by-day activities with locations, categories, and estimated costs
- Downloadable JSON itinerary
- Google Gemini API key kept in Streamlit secrets

## Technology

- Python 3.10+
- Streamlit
- FastAPI/Pydantic itinerary service reused from `backend/`
- Google Gen AI Python SDK
- Gemini `gemini-3.8-flash` by default

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and select **Create app**.
3. Choose this repository, the `master` branch, and `streamlit_app.py` as the **Main file path**.
4. Open the app's **Settings → Secrets** and add your Gemini API key:

   ```toml
   GEMINI_API_KEY = "your-Gemini-API-key"
   GEMINI_MODEL = "gemini-3.8-flash"
   ```

5. Select **Deploy**. When the deployment completes, open the Streamlit URL.

Create a key in [Google AI Studio](https://aistudio.google.com/apikey). Keep it in Streamlit secrets; do not commit it to GitHub or expose it in frontend variables. If you already deployed the app with another model, change `GEMINI_MODEL` in **Settings → Secrets**, save, and reboot/redeploy the app.

The recommended model is **`gemini-3.8-flash`**: Google's current model documentation lists it as stable and supports structured output. Older model IDs may be retired or unavailable to your API project. Confirm current model availability and limits in [Gemini model documentation](https://ai.google.dev/gemini-api/docs/models) and [API pricing](https://ai.google.dev/gemini-api/docs/pricing).

## Run locally

From the repository root in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY = "your-Gemini-API-key"
$env:GEMINI_MODEL = "gemini-3.8-flash"
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Troubleshooting

- **HTTP 400 from Gemini:** Update the app to the latest commit and reboot it. The app sends Gemini a simplified JSON schema and validates the response locally. If the error persists, check the Streamlit deployment logs for the provider's detailed error; HTTP 400 can indicate an invalid request or schema, not just an unavailable model.
- **Model unavailable or not found:** Check that the model ID is spelled exactly as above and is available to your Google AI Studio project and region.
- **Quota or rate limit:** Review your Gemini project's limits and billing/availability in Google AI Studio.
- **App does not see a secret:** Confirm the secrets are valid TOML, saved under the deployed app's settings, and use the exact `GEMINI_API_KEY` spelling.

Prices, opening hours, and suggestions in generated itineraries are estimates, not verified or bookable offers. Check important travel details with the provider before relying on them.

## Original full-stack application

The repository also contains the original React/Vite frontend, FastAPI API, and optional Supabase authentication and saved-trip support. That setup needs separate frontend and backend hosting plus Supabase configuration; it is not required for the Streamlit deployment above.
