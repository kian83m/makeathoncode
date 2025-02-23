from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import speech_recognition as sr
import openai 
from google.cloud import speech
from pydub import AudioSegment
import io
import os
import datetime


app = Flask(__name__)

# Initialize Firebase Admin SDK.
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)

# Initialize Firestore DB.
db = firestore.client()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# -----------------------------------
# User Endpoints
# -----------------------------------
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"error": "Missing required field: 'user_id'"}), 400

    user_id = data['user_id']
    user_ref = db.collection('users').document(user_id)
    if user_ref.get().exists:
        return jsonify({"error": "User already exists"}), 400

    user_ref.set({"user_id": user_id})
    return jsonify({"message": f"User '{user_id}' added successfully"}), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    users = db.collection('users').stream()
    results = [{"user_id": user.id} for user in users]
    return jsonify(results), 200

@app.route('/api/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        return jsonify({"error": "User not found"}), 404

    conversations = db.collection('conversations').where('user_id', '==', user_id).stream()
    for conv in conversations:
        conv.reference.delete()

    user_ref.delete()
    return jsonify({"message": f"User '{user_id}' and their conversations deleted successfully"}), 200

# -----------------------------------
# Conversation Endpoints
# -----------------------------------
@app.route('/api/user/<string:user_id>/conversation', methods=['POST'])
def add_user_conversation(user_id):
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        return jsonify({"error": f"User '{user_id}' not found. Please add the user first."}), 404

    data = request.get_json()
    if not data or 'user_message' not in data or 'assistant_message' not in data:
        return jsonify({"error": "Missing required fields: 'user_message' and 'assistant_message'"}), 400

    conversation_data = {
        "user_id": user_id,
        "user_message": data['user_message'],
        "assistant_message": data['assistant_message']
    }
    conv_ref = db.collection('conversations').add(conversation_data)
    conversation_id = conv_ref[1].id
    return jsonify({
        "message": f"Conversation for user '{user_id}' logged successfully",
        "id": conversation_id,
        "user_id": user_id,
        "user_message": data['user_message'],
        "assistant_message": data['assistant_message']
    }), 200

@app.route('/api/user/<string:user_id>/conversations', methods=['GET'])
def get_user_conversations(user_id):
    conversations = db.collection('conversations').where('user_id', '==', user_id).stream()
    results = []
    found = False
    for conv in conversations:
        found = True
        conv_data = conv.to_dict()
        conv_data["id"] = conv.id
        results.append(conv_data)
    if not found:
        return jsonify({"error": "No conversations found for this user"}), 404

    return jsonify(results), 200

@app.route('/api/user/<string:user_id>/conversations', methods=['DELETE'])
def delete_user_conversations(user_id):
    conversations = db.collection('conversations').where('user_id', '==', user_id).stream()
    found = False
    for conv in conversations:
        found = True
        conv.reference.delete()
    if not found:
        return jsonify({"error": "No conversations found for this user"}), 404

    return jsonify({"message": f"All conversations for user '{user_id}' deleted successfully"}), 200

@app.route('/api/user/<string:user_id>/conversation/<string:conversation_id>', methods=['DELETE'])
def delete_specific_conversation(user_id, conversation_id):
    conv_ref = db.collection('conversations').document(conversation_id)
    conv_doc = conv_ref.get()
    if not conv_doc.exists or conv_doc.to_dict().get("user_id") != user_id:
        return jsonify({"error": "Conversation not found for this user"}), 404

    conv_ref.delete()
    return jsonify({"message": f"Conversation with ID {conversation_id} for user '{user_id}' deleted successfully"}), 200

def get_chatgpt_response(user_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a compassionate and insightful therapist who also functions as a voice assistant. Provide supportive, thoughtful, and helpful responses to the user's input."},
            {"role": "user", "content": user_text}
        ]
    )
    assistant_text = response.choices[0].message.content
    return assistant_text

def get_stress_level(user_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an empathetic mental health assistant specializing in stress analysis. "
                    "Analyze the user's input to determine the user's stress level on a scale from 0 to 100, "
                    "where 0 means no stress and 100 means extreme stress. Provide a concise explanation "
                    "of the factors contributing to the stress assessment, and then end your response with a line "
                    "in the following format: 'Stress Level: X/100' where X is the numerical value."
                )
            },
            {"role": "user", "content": user_text}
        ]
    )
    stress_response = response.choices[0].message.content
    return stress_response


# Updated audio endpoint creates a new conversation with auto-generated ID.
@app.route('/api/user/<string:user_id>/audio', methods=['POST'])
def process_audio(user_id):
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        return jsonify({"error": f"User '{user_id}' not found. Please add the user first."}), 404

    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['file']
    original_audio = AudioSegment.from_file(audio_file, format="wav")
    if original_audio.channels != 1:
        mono_audio = original_audio.set_channels(1)
    else:
        mono_audio = original_audio

    buf = io.BytesIO()
    mono_audio.export(buf, format="wav")
    buf.seek(0)
    audio_content = buf.read()

    speech_client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,  # Update if necessary for your audio file.
        language_code="en-US"
    )

    try:
        response = speech_client.recognize(config=config, audio=audio)
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    transcript = " ".join([result.alternatives[0].transcript for result in response.results]).strip()
    gpt_response = get_chatgpt_response(transcript)
    stress_level = get_stress_level(transcript)

    timestamp_str = datetime.datetime.utcnow().isoformat() + 'Z'

    conversation_data = {
        "user_id": user_id,
        "user_message": transcript,
        "assistant_message": gpt_response,
        "stress_response": stress_level,
        "timestamp": timestamp_str
    }

    # Create a new conversation document with an auto-generated ID.
    conv_ref = db.collection('conversations').add(conversation_data)
    conversation_id = conv_ref[1].id

    return jsonify({
        "message": "Conversation created successfully",
        "id": conversation_id,
        "user_id": user_id,
        "user_message": transcript,
        "assistant_message": gpt_response,
        "stress_response": stress_level,
        "timestamp": timestamp_str
    }), 200

@app.route('/api/user/<string:user_id>/text', methods=['POST'])
def process_text(user_id):
    # Verify the user exists.
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        return jsonify({"error": f"User '{user_id}' not found. Please add the user first."}), 404

    data = request.get_json()
    if not data or 'user_message' not in data:
        return jsonify({"error": "Missing required field: 'user_message'"}), 400

    user_message = data['user_message']

    # Generate the assistant response using GPT.
    gpt_response = get_chatgpt_response(user_message)
    # Determine stress level from the user's text.
    stress_level = get_stress_level(user_message)

    # Get current UTC time as ISO string.
    timestamp_str = datetime.datetime.utcnow().isoformat() + 'Z'

    conversation_data = {
        "user_id": user_id,
        "user_message": user_message,
        "assistant_message": gpt_response,
        "stress_response": stress_level,
        "timestamp": timestamp_str
    }

    # Create a new conversation document with an auto-generated ID.
    conv_ref = db.collection('conversations').add(conversation_data)
    conversation_id = conv_ref[1].id

    return jsonify({
        "message": "Conversation created successfully",
        "id": conversation_id,
        "user_id": user_id,
        "user_message": user_message,
        "assistant_message": gpt_response,
        "stress_response": stress_level,
        "timestamp": timestamp_str
    }), 200

@app.route('/api/user/<string:user_id>/stats/week-streak', methods=['GET'])
def get_week_streak(user_id):
    convs = db.collection('conversations').where('user_id', '==', user_id).stream()
    dates = set()
    for conv in convs:
        data = conv.to_dict()
        if "timestamp" in data:
            ts = data["timestamp"]
            # If the timestamp is a string, process it accordingly.
            if isinstance(ts, str):
                if ts.endswith("Z"):
                    ts = ts[:-1]
                try:
                    dt = datetime.datetime.fromisoformat(ts)
                except Exception:
                    continue
            # If it's a datetime object, use it directly.
            elif isinstance(ts, datetime.datetime):
                dt = ts
            else:
                continue
            dates.add(dt.date())

    if not dates:
        return jsonify({"week_streak": 0}), 200

    sorted_dates = sorted(dates, reverse=True)
    streak = 1
    current_date = sorted_dates[0]
    for d in sorted_dates[1:]:
        if (current_date - d).days == 1:
            streak += 1
            current_date = d
        else:
            break

    return jsonify({"week_streak": streak}), 200

@app.route('/api/user/<string:user_id>/stats/days-conversed', methods=['GET'])
def get_days_conversed(user_id):
    convs = db.collection('conversations').where('user_id', '==', user_id).stream()
    dates = set()
    for conv in convs:
        data = conv.to_dict()
        if "timestamp" in data:
            ts = data["timestamp"]
            if isinstance(ts, str):
                if ts.endswith("Z"):
                    ts = ts[:-1]
                try:
                    dt = datetime.datetime.fromisoformat(ts)
                except Exception:
                    continue
            elif isinstance(ts, datetime.datetime):
                dt = ts
            else:
                continue
            dates.add(dt.date())
    return jsonify({"days_conversed": len(dates)}), 200


# Endpoint to get the total number of words spoken by the user across all conversations.
@app.route('/api/user/<string:user_id>/stats/total-words', methods=['GET'])
def get_total_words(user_id):
    convs = db.collection('conversations').where('user_id', '==', user_id).stream()
    total_words = 0
    for conv in convs:
        data = conv.to_dict()
        if "user_message" in data:
            total_words += len(data["user_message"].split())
    return jsonify({"total_words": total_words}), 200

@app.route('/api/user/<string:user_id>/summary/<string:date_str>', methods=['GET'])
def get_daily_summary(user_id, date_str):
    # Parse the provided date (assumes format MM-DD-YYYY)
    try:
        target_date = datetime.datetime.strptime(date_str, "%m-%d-%Y").date()
    except Exception as e:
        return jsonify({"error": "Invalid date format. Please use MM-DD-YYYY."}), 400

    # Retrieve all conversation documents for the user.
    convs = db.collection('conversations').where('user_id', '==', user_id).stream()
    assistant_messages = []
    for conv in convs:
        data = conv.to_dict()
        if "timestamp" in data and "assistant_message" in data:
            ts = data["timestamp"]
            dt = None
            # If the timestamp is a string, process it accordingly.
            if isinstance(ts, str):
                if ts.endswith("Z"):
                    ts = ts[:-1]
                try:
                    dt = datetime.datetime.fromisoformat(ts).date()
                except Exception:
                    continue
            # If it's a datetime object, use it directly.
            elif isinstance(ts, datetime.datetime):
                dt = ts.date()
            else:
                continue
            if dt == target_date:
                assistant_messages.append(data["assistant_message"])

    if not assistant_messages:
        return jsonify({"error": f"No conversations found on {date_str} for user '{user_id}'"}), 404

    # Combine all assistant responses into one block of text.
    combined_text = "\n".join(assistant_messages)
    prompt = (
        "Summarize the following assistant responses into exactly one concise sentence. "
        "The summary must be a single sentence without multiple sentences or extra punctuation. "
        "Only output the sentence without any explanation.\n\n"
        f"Assistant responses:\n{combined_text}\n\nSummary:"
    )

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert summarizer."},
                {"role": "user", "content": prompt}
            ]
        )
    except Exception as e:
        return jsonify({"error": f"GPT summary failed: {str(e)}"}), 500

    summary = response.choices[0].message.content.strip()

    return jsonify({
        "date": date_str,
        "summary": summary
    }), 200


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)