from flask import Flask, render_template, request, jsonify, Response
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        english_text = data.get('text', '').strip()
        
        if not english_text:
            return jsonify({'error': 'Please enter some text'}), 400
        
        print(f"Input text: {english_text}")
        
        try:
            # Translate from English to Kannada using deep-translator
            translator = GoogleTranslator(source='en', target='kn')
            kannada_text = translator.translate(english_text)
            
            print(f"Translated text: {kannada_text}")
            
            if not kannada_text:
                return jsonify({'error': 'Translation returned empty result'}), 500
            
            return jsonify({
                'success': True,
                'kannada_text': kannada_text,
                'character_count': len(kannada_text)
            })
        except Exception as trans_error:
            print(f"Translation exception: {trans_error}")
            import traceback
            traceback.print_exc()
            raise trans_error
    
    except Exception as e:
        print(f"Translation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Translation error: {str(e)}'}), 500

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        kannada_text = data.get('text', '').strip()
        
        if not kannada_text:
            return jsonify({'error': 'No Kannada text provided'}), 400
        
        print(f"TTS Input: {kannada_text}")
        
        # Generate speech using gTTS
        tts = gTTS(text=kannada_text, lang='kn', slow=False)
        
        # Save to bytes
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        
        # Convert to base64
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
        
        print(f"Audio generated successfully, size: {len(audio_base64)}")
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'message': 'Audio generated successfully'
        })
        
    except Exception as e:
        print(f"TTS error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Text-to-speech error: {str(e)}'}), 500


@app.route('/text-to-speech-file', methods=['POST'])
def text_to_speech_file():
    try:
        data = request.get_json()
        kannada_text = data.get('text', '').strip()
        if not kannada_text:
            return jsonify({'error': 'No Kannada text provided'}), 400

        # Generate speech using gTTS and return raw MP3 bytes
        tts = gTTS(text=kannada_text, lang='kn', slow=False)
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        audio_bytes = audio_file.read()

        resp = Response(audio_bytes, mimetype='audio/mpeg')
        resp.headers['Content-Length'] = str(len(audio_bytes))
        resp.headers['Content-Disposition'] = 'inline; filename="kannada.mp3"'
        return resp

    except Exception as e:
        print(f"TTS file error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Text-to-speech error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
