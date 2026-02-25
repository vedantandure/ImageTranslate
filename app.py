# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
from deep_translator import GoogleTranslator
import os
from database import init_db, save_translation, get_history


app = Flask(__name__)
CORS(app)

reader = easyocr.Reader(['en'])

# Start database when app starts
init_db()

@app.route('/translate', methods=['POST'])
def translate():

    if 'image' not in request.files:
        return jsonify({"error": "No image sent"}), 400

    image = request.files['image']
    image_path = 'uploads/' + image.filename
    os.makedirs('uploads', exist_ok=True)
    image.save(image_path)

    result = reader.readtext(image_path)
    text = " ".join([item[1] for item in result])

    if not text.strip():
        return jsonify({"error": "No text found in image"}), 400

    print("Detected Text:", text)

    languages = {
        "English": "en",
        "Hindi": "hi",
        "German": "de",
        "Spanish": "es",
        "French": "fr"
    }

    translations = {}
    for lang_name, lang_code in languages.items():
        translated = GoogleTranslator(source='auto', target=lang_code).translate(text)
        translations[lang_name] = translated

    # ✅ Save to database
    save_translation(image.filename, text, translations)
    print("Saved to database!")

    return jsonify({
        "status": "success",
        "extracted_text": text,
        "translations": translations
    })


# ✅ History route
@app.route('/history', methods=['GET'])
def history():
    rows = get_history()
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "image_name": row[1],
            "extracted_text": row[2],
            "english": row[3],
            "hindi": row[4],
            "german": row[5],
            "spanish": row[6],
            "french": row[7],
            "timestamp": row[8]
        })
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)