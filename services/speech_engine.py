import os
from gtts import gTTS

class SpeechEngine:
    @staticmethod
    def generate_tamil_audio(text_ta: str, output_path: str = "static/response.mp3"):
        """
        Converts Tamil text into an MP3 file with safe error handling.
        """
        if not text_ta:
            text_ta = "தகவல்கள் கிடைக்கவில்லை."

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            tts = gTTS(text=text_ta, lang='ta', slow=False)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"[Warning] gTTS audio generation skipped: {e}")
            return None