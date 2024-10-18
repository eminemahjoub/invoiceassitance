import os
import wave
import pyaudio
import vosk
import pyttsx3
from fpdf import FPDF
from datetime import datetime
import atexit

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.setProperty('voice', 'en')  # Default to English voice
    engine.say(text)
    engine.runAndWait()

# Cleanup function to stop the engine before exiting
def cleanup():
    engine.stop()

atexit.register(cleanup)

# Set up speech recognition
class VoskRecognizer:
    def __init__(self, model_path):
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

    def recognize(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        print("Listening...")
        data = b""
        while True:
            chunk = stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(chunk):
                data += chunk
            else:
                data += chunk

            if len(data) > 16000 * 5:  # Limit listening to 5 seconds
                break

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Write data to audio.wav
        with wave.open('audio.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(data)

        # Recognize audio
        with wave.open('audio.wav', 'rb') as wf:
            self.recognizer = vosk.KaldiRecognizer(self.model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if self.recognizer.AcceptWaveform(data):
                    break
            
            result = self.recognizer.Result()
            try:
                result_json = eval(result)  # Convert string to dictionary
                return result_json
            except SyntaxError:
                return {"text": result}  # In case of an error, return the raw result

# Invoice generation function
def generate_invoice(client_name, amount, items):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Invoice", ln=True, align='C')

    # Invoice Details
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(100, 10, txt=f"Client: {client_name}", ln=True)
    pdf.cell(100, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(100, 10, txt=f"Amount: {amount} USD", ln=True)

    # Items
    pdf.ln(10)
    pdf.cell(100, 10, txt="Items:", ln=True)
    for item in items:
        pdf.cell(100, 10, txt=f"- {item}", ln=True)

    # Save PDF
    filename = f"{client_name}_invoice.pdf"
    pdf.output(filename)
    speak(f"Invoice for {client_name} has been generated and saved as {filename}.")
    print(f"Invoice saved as {filename}")

# Main function
def main():
    model_path = "/home/joyboy/invoiceassitance/myenv/vosk-model-small-en-us-0.15"  # Your model path
    recognizer = VoskRecognizer(model_path)

    speak("Hello! What would you like to do today?")
    command_result = recognizer.recognize()
    command_text = command_result.get('text', '')

    # Log the recognized command
    print(f"Recognized command: {command_text}")

    if "invoice" in command_text.lower():
        speak("Great! I can help you create an invoice. What is the client's name?")
        client_name_result = recognizer.recognize()
        client_name = client_name_result.get('text', '')

        speak("What is the amount?")
        amount_result = recognizer.recognize()
        amount = amount_result.get('text', '')

        speak("What items are included? Please say 'done' when you are finished.")
        items = []
        while True:
            item_result = recognizer.recognize()
            item = item_result.get('text', '')
            if item.lower() == "done":
                break
            items.append(item)

        generate_invoice(client_name, amount, items)
    else:
        speak("I'm sorry, I can only help you with creating invoices right now.")
    model_path = "/home/joyboy/invoiceassitance/myenv/vosk-model-small-en-us-0.15"  
    recognizer = VoskRecognizer(model_path)

    speak("Hello! What would you like to do today?")
    command_result = recognizer.recognize()
    command_text = command_result.get('text', '')

    if "invoice" in command_text.lower():
        speak("Great! I can help you create an invoice. What is the client's name?")
        client_name_result = recognizer.recognize()
        client_name = client_name_result.get('text', '')

        speak(f"You said the client's name is {client_name}. Is that correct?")
        confirmation_result = recognizer.recognize()
        confirmation_text = confirmation_result.get('text', '')

        if "yes" in confirmation_text.lower():
            speak("What is the amount?")
            amount_result = recognizer.recognize()
            amount = amount_result.get('text', '')

            speak(f"You said the amount is {amount}. Is that correct?")
            amount_confirmation = recognizer.recognize()
            amount_confirmation_text = amount_confirmation.get('text', '')

            if "yes" in amount_confirmation_text.lower():
                speak("What items are included? Please say 'done' when you are finished.")
                items = []

                while True:
                    item_result = recognizer.recognize()
                    item = item_result.get('text', '')

                    if item.lower() == "done":
                        break

                    items.append(item)
                    # Confirm each item
                    speak(f"You added {item}. Say another item or 'done' if you are finished.")

                # Generate the invoice after all items are collected
                generate_invoice(client_name, amount, items)
            else:
                speak("Let's try again. What is the amount?")
        else:
            speak("Let's try again. What is the client's name?")
    else:
        speak("I'm sorry, I can only help you with creating invoices right now.")

if __name__ == "__main__":
    main()
