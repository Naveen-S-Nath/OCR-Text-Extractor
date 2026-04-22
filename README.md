# 🧠 OCR Based Text Extractor

A Flask-based web application that extracts text from handwritten images using OCR and enhances it using AI-powered processing.

---

## 📸 Demo

### 🏠 Home Page

<p align="center">
  <img width="1681" height="850" alt="image" src="https://github.com/user-attachments/assets/548ebcad-84bc-4b90-8e92-eeddb3fda297" />
" />
</p>

### 📤 Upload Page

<p align="center">
  <img width="772" height="537" alt="image" src="https://github.com/user-attachments/assets/5e56ac3d-071e-418d-baa4-4d8df99e7aad" />
" />
</p>

---

## 🚀 Features

* 📷 Upload handwritten images (JPG/PNG)
* 🔍 Extract text using EasyOCR
* ✨ AI-based text correction (optional)
* ❓ Automatically detects questions
* 🤖 Generates answers using Gemini API (if configured)
* 📥 Download processed text output

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **OCR Engine:** EasyOCR
* **Image Processing:** OpenCV, NumPy
* **AI Processing:** Google Gemini API (optional)
* **Frontend:** HTML, CSS

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ocr-text-extractor.git
cd ocr-text-extractor
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Add Gemini API Key

Create a `.env` file in the root directory:

```
GEMINI_API_KEY=your_api_key_here
```

> ⚠️ AI features (text correction & Q&A) require a valid API key.

### 4️⃣ Run the application

```bash
python app.py
```

### 5️⃣ Open in browser

```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
├── app.py
├── requirements.txt
├── templates/
├── static/
├── .gitignore
```

---

## ⚠️ Notes

* EasyOCR models may download during first run.
* AI features are optional and require a Gemini API key.
* Sensitive files and large models are excluded using `.gitignore`.

---

## 💡 Future Improvements

* Add authentication system
* Improve UI/UX
* Support multiple languages
* Optimize model performance for deployment

---



**Naveen S Nath**
