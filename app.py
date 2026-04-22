import os
import uuid
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file,
    flash,
)
import easyocr
import io
import google.generativeai as genai
from dotenv import load_dotenv

# --- NEW IMPORTS ---
# These are needed for the robust image loading fix
import numpy as np
import cv2 
# ---------------------

# --- Configuration ---
app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- Gemini API Configuration ---
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Gemini AI model loaded successfully.")
except Exception as e:
    print(f"❌ CRITICAL: Failed to initialize Gemini: {e}")
    gemini_model = None

# --- OCR Engine Initialization ---
print("Loading EasyOCR models... (This may take a moment on first run)")
try:
    ocr_reader = easyocr.Reader(['en'], gpu=False)
    print("✅ EasyOCR engine initialized successfully.")
except Exception as e:
    print(f"❌ CRITICAL: Failed to initialize EasyOCR: {e}")
    ocr_reader = None


# --- UPDATED FUNCTION ---
def perform_ocr(image_path):
    """
    Performs OCR on a given image file and returns the extracted text.
    """
    if not ocr_reader:
        return "Error: OCR engine failed to load."

    try:
        # --- THIS IS THE FIX ---
        # Instead of passing the path, we read the bytes manually.
        # This is more robust for tricky files from WhatsApp.
        
        # 1. Read the file as raw bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        # 2. Convert the bytes to a numpy array
        np_arr = np.frombuffer(image_bytes, np.uint8)
        
        # 3. Decode the numpy array into an OpenCV image
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        # --- END OF FIX ---

        # Check if image decoding failed (e.g., still corrupted)
        if img_cv is None:
            return "Error: Could not decode the image. The file might be corrupted."

        # Pass the decoded image (as a numpy array) to EasyOCR
        result = ocr_reader.readtext(img_cv)
        
        text_list = [item[1] for item in result]
        
        return "\n".join(text_list)

    except Exception as e:
        print(f"An OCR error occurred: {e}")
        return f"Error processing file: {e}"
    finally:
        # Clean up the original uploaded file
        if os.path.exists(image_path):
            os.remove(image_path)
# --- END OF UPDATED FUNCTION ---


def call_gemini_api(raw_text):
    """
    Sends raw OCR text to Gemini and expects a structured response.
    """
    if not gemini_model:
        return "Error: Gemini model is not configured."
    if not raw_text.strip():
        return raw_text # Return raw text if it's just whitespace

    # --- THIS IS THE NEW, STRICT PROMPT ---
    prompt = f"""
    You are a text-processing API. Your response format is EXTREMELY IMPORTANT.
    You will be given raw OCR text.

    1.  First, correct the OCR text. Fix misspellings, random symbols, and errors based on context. This is the "Corrected Text".
    2.  Second, check if this "Corrected Text" is a question.
    3.  You MUST respond in one of two formats:

    **Format 1 (If it is NOT a question):**
    Return *only* the "Corrected Text". Do not add any other words, explanations, or labels.

    **Format 2 (If it IS a question):**
    Return the "Corrected Text", followed by the delimiter '|||ANSWER|||', followed by your answer.
    
    Example for Format 2:
    Who was the fir5t pres-ident?
    |||ANSWER|||
    The first president of the United States was George Washington.

    ---
    RAW OCR TEXT:
    {raw_text}
    """

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return f"Error during Gemini processing: {e}"


# --- Flask Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload")
def upload_page():
    return render_template("input.html")

@app.route("/process", methods=["POST"])
def process_image():
    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(request.url)
    
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file.")
        return redirect(url_for('upload_page'))
    
    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Step 1: Get the raw text from OCR
        raw_ocr_text = perform_ocr(filepath)
        
        # Step 2: Send the raw text to Gemini for enhancement
        gemini_response = call_gemini_api(raw_ocr_text) # This was a typo, fixed to call_gemini_api
        
        # --- NEW PARSING LOGIC ---
        corrected_text = ""
        answer = None # Default to None

        if "|||ANSWER|||" in gemini_response:
            # It's a question, split it
            parts = gemini_response.split("|||ANSWER|||", 1)
            corrected_text = parts[0].strip()
            answer = parts[1].strip()
        else:
            # Not a question, the whole response is the corrected text
            corrected_text = gemini_response.strip()

        # --- SAVE ALL 3 PIECES ---
        session["raw_text"] = raw_ocr_text
        session["corrected_text"] = corrected_text
        session["answer"] = answer # This will be None or the answer string
        
        return redirect(url_for("result_page"))
    
    flash("Could not process the input. Please try again.")
    return redirect(url_for("index"))

@app.route("/result")
def result_page():
    """Fetches all 3 text parts and sends them to the template."""
    raw_text = session.get("raw_text", "No raw text found.")
    corrected_text = session.get("corrected_text", "No corrected text found.")
    answer = session.get("answer", None) # Get answer, default to None
    
    return render_template(
        "result.html", 
        raw_text=raw_text, 
        corrected_text=corrected_text, 
        answer=answer
    )

@app.route("/download")
def download_text():
    """Formats all 3 text parts for download."""
    raw = session.get("raw_text", "")
    corrected = session.get("corrected_text", "")
    answer = session.get("answer", None)

    # Build the text file content
    text_to_download = f"--- RAW OCR TEXT ---\n{raw}\n\n"
    text_to_download += f"--- AI-ENHANCED TEXT ---\n{corrected}\n"

    if answer:
        text_to_download += f"\n--- AI ANSWER ---\n{answer}\n"

    buffer = io.BytesIO()
    buffer.write(text_to_download.encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="enhanced_text.txt",
        mimetype="text/plain",
    )

if __name__ == "__main__":
    app.run(debug=True)