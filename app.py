"""
AI Driver Monitor — Flask Backend
- Serves the static PWA (index.html, sw.js, manifest.json, icons/, static/)
- Provides REST API for Emergency Contact management
  GET    /api/contact          → fetch saved contact
  POST   /api/contact          → create or update contact
  DELETE /api/contact          → remove contact
  PATCH  /api/contact/toggle   → flip enabled flag

All AI detection runs in the browser (MediaPipe). This server only handles
persistence and Twilio SMS notifications.
"""

import os
import re
from datetime import datetime, timezone
from urllib.parse import quote

import phonenumbers
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file (if it exists)
load_dotenv()

# ─── APP SETUP ───────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=".", static_url_path="")

# Database: use DATABASE_URL env var for production (PostgreSQL on Render),
# fall back to local SQLite for development.
database_url = os.environ.get("DATABASE_URL", "sqlite:///driver.db")

# Render provides postgres:// URIs; SQLAlchemy 1.4+ requires postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ─── MODEL ───────────────────────────────────────────────────────────────────
class EmergencyContact(db.Model):
    """
    Stores a single emergency contact for the driver.
    One row per deployment instance (id is always 1).
    """
    __tablename__ = "emergency_contact"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    phone        = db.Column(db.String(20),  nullable=False)   # E.164 format
    relationship = db.Column(db.String(80),  nullable=True)
    enabled      = db.Column(db.Boolean,     nullable=False, default=True)
    created_at   = db.Column(db.DateTime,    nullable=False,
                             default=lambda: datetime.now(timezone.utc))
    updated_at   = db.Column(db.DateTime,    nullable=False,
                             default=lambda: datetime.now(timezone.utc),
                             onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id":           self.id,
            "name":         self.name,
            "phone":        self.phone,
            "relationship": self.relationship,
            "enabled":      self.enabled,
            "created_at":   self.created_at.isoformat(),
            "updated_at":   self.updated_at.isoformat(),
        }


# Create tables on startup (no-op if they already exist)
with app.app_context():
    db.create_all()


# ─── STATE ───────────────────────────────────────────────────────────────────
# In-memory tracking to prevent SMS spam.
# If we deploy to multiple instances, this should move to Redis or the DB.
app_state = {
    "last_sms_sent": None
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def validate_e164(raw: str):
    """
    Validates and normalises a phone number to E.164 format.
    Returns (normalised_string, None) on success or (None, error_message) on failure.
    """
    try:
        parsed = phonenumbers.parse(raw, None)   # raw must include country code (+)
        if not phonenumbers.is_valid_number(parsed):
            return None, "Phone number is not valid."
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164), None
    except phonenumbers.phonenumberutil.NumberParseException:
        return None, (
            "Could not parse phone number. "
            "Please include the country code, e.g. +919876543210"
        )


def error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status


def ok(data: dict, status: int = 200):
    return jsonify({"ok": True, **data}), status


# ─── API ROUTES ──────────────────────────────────────────────────────────────

@app.route("/api/contact", methods=["GET"])
def get_contact():
    """Return the saved emergency contact, or 404 if none exists."""
    contact = db.session.get(EmergencyContact, 1)
    if contact is None:
        return ok({"contact": None}, status=200)
    return ok({"contact": contact.to_dict()})


@app.route("/api/contact", methods=["POST"])
def upsert_contact():
    """
    Create or update the emergency contact.
    Body (JSON):
      name         – string, required
      phone        – string, required, must be parseable E.164
      relationship – string, optional
      enabled      – bool, optional (default True)
    """
    body = request.get_json(silent=True)
    if not body:
        return error("Request body must be JSON.")

    name = (body.get("name") or "").strip()
    phone_raw = (body.get("phone") or "").strip()
    relationship = (body.get("relationship") or "").strip() or None
    enabled = bool(body.get("enabled", True))

    # Validate required fields
    if not name:
        return error("'name' is required.")
    if len(name) > 120:
        return error("'name' must be 120 characters or fewer.")
    if not phone_raw:
        return error("'phone' is required.")

    phone_e164, phone_err = validate_e164(phone_raw)
    if phone_err:
        return error(phone_err)

    contact = db.session.get(EmergencyContact, 1)

    if contact is None:
        contact = EmergencyContact(
            id=1,
            name=name,
            phone=phone_e164,
            relationship=relationship,
            enabled=enabled,
        )
        db.session.add(contact)
    else:
        contact.name         = name
        contact.phone        = phone_e164
        contact.relationship = relationship
        contact.enabled      = enabled
        contact.updated_at   = datetime.now(timezone.utc)

    db.session.commit()
    return ok({"contact": contact.to_dict()}, status=201)


@app.route("/api/contact", methods=["DELETE"])
def delete_contact():
    """Remove the emergency contact entirely."""
    contact = db.session.get(EmergencyContact, 1)
    if contact is None:
        return error("No emergency contact is saved.", 404)
    db.session.delete(contact)
    db.session.commit()
    return ok({"message": "Emergency contact deleted."})


@app.route("/api/contact/toggle", methods=["PATCH"])
def toggle_contact():
    """Flip the enabled flag on the existing contact."""
    contact = db.session.get(EmergencyContact, 1)
    if contact is None:
        return error("No emergency contact is saved.", 404)
    contact.enabled    = not contact.enabled
    contact.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return ok({"contact": contact.to_dict()})


@app.route("/api/trigger-alarm", methods=["POST"])
def trigger_alarm():
    """
    Triggered by the frontend when a critical alarm occurs (Drowsy or Yawn).
    Sends an SMS and places a voice call via Twilio if a contact is saved and
    enabled, subject to a 30-second cooldown.
    Voice and SMS share the same cooldown and use the same emergency contact.
    """
    # 1. Check if contact exists and is enabled
    contact = db.session.get(EmergencyContact, 1)
    if contact is None or not contact.enabled:
        return ok({"message": "No action taken. Contact missing or disabled."})

    # 2. Check cooldown (30 seconds)
    now = datetime.now(timezone.utc)
    if app_state["last_sms_sent"]:
        time_since_last = (now - app_state["last_sms_sent"]).total_seconds()
        if time_since_last < 30:  # 30 seconds
            return ok({
                "message": "Cooldown active. No SMS sent.",
                "cooldown_remaining_sec": int(30 - time_since_last)
            })

    # 3. Check Twilio config
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print("[WARNING] SMS requested, but Twilio credentials are not fully configured in environment.")
        return error("Twilio is not configured.", 500)

    # 4. Send SMS
    try:
        client = Client(account_sid, auth_token)
        body_text = "sms_appointment_reminders"
        
        message = client.messages.create(
            body=body_text,
            from_=from_number,
            to=contact.phone
        )
        print(f"[INFO] SMS Sent to {contact.phone}. SID: {message.sid}")

        # Update cooldown timer (shared for both SMS and voice call)
        app_state["last_sms_sent"] = now

        # 5. Place emergency voice call (independent — SMS success is preserved
        #    even if the call fails)
        #    Uses Twilio-hosted TTS template (Trial-compatible, no external server needed)
        call_sid = None
        call_error = None
        try:
            voice_message = (
                "Emergency alert. The AI Driver Monitor has detected possible "
                "driver drowsiness. Please contact the driver immediately."
            )
            tts_url = (
                "https://webhooks.twilio.com/v1/Voice/Template/voice_text_to_speech"
                f"?VoiceMessage={quote(voice_message)}"
            )
            call = client.calls.create(
                url=tts_url,
                from_=from_number,
                to=contact.phone
            )
            call_sid = call.sid
            print(f"[INFO] Voice call initiated to {contact.phone}. SID: {call_sid}")
        except Exception as call_exc:
            # Log the failure but do NOT expose credentials
            call_error = str(call_exc)
            print(f"[ERROR] Voice call failed: {call_error}")

        response_payload = {
            "message": "SMS and voice call sent successfully." if call_sid else "SMS sent. Voice call failed.",
            "sms_sid": message.sid,
        }
        if call_sid:
            response_payload["call_sid"] = call_sid
        if call_error:
            response_payload["call_error"] = call_error

        return ok(response_payload)

    except Exception as e:
        print(f"[ERROR] Failed to send SMS: {e}")
        return error(f"Failed to send SMS: {str(e)}", 500)


# ─── STATIC FILE SERVING ─────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_file("index.html")


@app.route("/<path:path>")
def serve_static(path):
    # Never expose the database file
    if path.endswith(".db") or path.endswith(".db-shm") or path.endswith(".db-wal"):
        return error("Not found.", 404)
    return send_from_directory(".", path)


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"[INFO] Starting AI Driver Monitor on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
