# 🛡️ CyberSentinel – Smart Detection of Fake News and Online Fraud

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white">
  <img src="https://img.shields.io/badge/DistilBERT-2563EB?style=for-the-badge&logo=huggingface&logoColor=white">
  <img src="https://img.shields.io/badge/LSTM-000000?style=for-the-badge&logoColor=white">
  <img src="https://img.shields.io/badge/CNN-1D-2563EB?style=for-the-badge">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flask-FFFFFF?style=for-the-badge&logo=flask&logoColor=black">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
</p>

<p align="center">
  <strong>An AI-powered cybersecurity platform designed to detect Fake News, Online Fraud, and Malicious URLs using Deep Learning and intelligent evidence retrieval.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-Powered-2563EB?style=flat-square">
  <img src="https://img.shields.io/badge/Deep_Learning-Enabled-000000?style=flat-square">
  <img src="https://img.shields.io/badge/Status-Active-FFFFFF?style=flat-square&labelColor=2563EB">
</p>

---

# 📖 Overview

**CyberSentinel** is an AI-powered cybersecurity platform developed to identify and analyze digital threats such as fake news, online fraud messages, and malicious URLs.

In today's digital world, misinformation, phishing messages, and fraudulent websites are becoming increasingly common. CyberSentinel combines **Artificial Intelligence, Deep Learning, and real-world news evidence retrieval** to help users identify potentially harmful digital content.

Unlike traditional rule-based detection systems, CyberSentinel uses specialized deep learning models to analyze different types of suspicious content.

The platform integrates three major detection modules:

- 📰 Fake News Detection using DistilBERT
- 📩 Online Fraud / SMS Detection using LSTM
- 🔗 Malicious URL Detection using 1D CNN

It also includes a News Evidence Retrieval module powered by the GNews API to retrieve related news articles and provide additional context for fake news verification.

---

# ✨ Key Features

- 📰 **Fake News Detection** – Identifies potentially misleading or fake news using DistilBERT.
- 📩 **Online Fraud Detection** – Analyzes suspicious SMS and messages using LSTM.
- 🔗 **Malicious URL Detection** – Classifies suspicious URLs using a 1D CNN model.
- 🔍 **Evidence-Based Verification** – Retrieves related news articles using the GNews API.
- 🧠 **Deep Learning Integration** – Uses specialized models for different cybersecurity tasks.
- ⚡ **Real-Time Prediction API** – Connects frontend interfaces with backend ML predictions.
- 📊 **Performance Dashboard** – Displays model evaluation and performance information.
- 🛡️ **Input Validation** – Validates user inputs before processing.
- 🔐 **Secure API Configuration** – Stores API credentials using environment variables.
- 🌐 **Interactive Web Interface** – Provides separate pages for different detection modules.

---

# 🧠 AI & Deep Learning Models

CyberSentinel uses three specialized deep learning architectures.

## 1. 📰 Fake News Detection – DistilBERT

**Model:** DistilBERT (Transformer-based architecture)

DistilBERT analyzes the contextual meaning and semantic relationships within news content.

**Working Process:**

1. User enters a news headline or article.
2. Input text is preprocessed and tokenized.
3. DistilBERT extracts contextual representations.
4. The classification layer predicts the news category.
5. The prediction is returned through the backend API.

**Purpose:** Identifying potentially misleading news based on textual context.

## 2. 📩 Online Fraud Detection – LSTM

**Model:** Long Short-Term Memory (LSTM)

LSTM is a type of recurrent neural network that learns sequential patterns in text.

**Working Process:**

1. User enters an SMS or suspicious message.
2. Text is cleaned and tokenized.
3. The sequence is passed into the LSTM network.
4. The model analyzes learned sequential patterns.
5. The system predicts whether the message is potentially fraudulent or legitimate.

**Purpose:** Detecting suspicious SMS messages and online fraud patterns.

## 3. 🔗 Malicious URL Detection – 1D CNN

**Model:** One-Dimensional Convolutional Neural Network (1D CNN)

The 1D CNN model identifies patterns in URL-related features to classify potentially malicious links.

**Working Process:**

1. User enters a URL.
2. The system extracts relevant URL features.
3. Extracted features are processed by the CNN model.
4. The model identifies suspicious patterns.
5. The system returns the URL classification.

**Purpose:** Identifying potentially malicious and suspicious URLs.

---

# 🔍 News Evidence Retrieval Module

CyberSentinel includes an additional **Evidence Retrieval and Verification Module** powered by the GNews API.

Instead of relying only on the deep learning prediction, this module searches for related real-world news reports to provide additional evidence.

### How It Works

1. User submits a news claim.
2. DistilBERT performs fake news classification.
3. The backend sends a separate evidence verification request.
4. The Evidence Retrieval service queries the GNews API.
5. Related articles and excerpts are retrieved.
6. The service evaluates available evidence.
7. Supporting or contradicting evidence is returned.

### Evidence Verdicts

- ✅ Supporting
- ❌ Contradicting
- ⚖️ Mixed
- 🔎 Insufficient

**Important:** Evidence retrieval and deep learning classification are separate processes. A related news article alone does not establish that a claim is true or false.

---

# 🏗️ System Architecture

CyberSentinel follows a frontend-backend-machine learning architecture.

```text
              USER
                |
                v
       CYBERSENTINEL WEB UI
                |
                v
         FRONTEND (VITE)
                |
                v
        FLASK REST API
                |
       +--------+--------+
       |        |        |
       v        v        v
    DistilBERT  LSTM    1D CNN
       |        |        |
       v        v        v
   Fake News  Fraud   Malicious
  Detection  Detection   URL
       |        |        |
       +--------+--------+
                |
                v
        PREDICTION RESULTS

       NEWS EVIDENCE SERVICE
                |
                v
            GNEWS API
                |
                v
       RELATED NEWS ARTICLES
                |
                v
       EVIDENCE VERIFICATION
```

---

# 🛠️ Technology Stack

## Frontend

- HTML5
- CSS3
- JavaScript
- Vite

## Backend

- Python
- Flask
- Flask REST API

## Artificial Intelligence & Deep Learning

- PyTorch
- DistilBERT
- LSTM
- 1D CNN
- Hugging Face Transformers

## External API

- GNews API

## Development Tools

- Visual Studio Code / Antigravity
- Git
- GitHub
- Node.js
- Python Virtual Environment

---

# 📂 Project Structure

```text
CyberSentinel/
│
├── backend/
│   ├── app.py
│   │
│   ├── services/
│   │   ├── evidence_service.py
│   │   └── input_classifier.py
│   │
│   └── tests/
│       ├── test_api.py
│       ├── test_evidence_service.py
│       └── test_fake_news_advanced.py
│
├── ml-pipeline/
│   ├── data/
│   ├── reports/
│   │
│   ├── scripts/
│   │   ├── 01_train_fake_news.py
│   │   ├── 02_train_fraud_sms.py
│   │   ├── 03_train_url.py
│   │   └── 04_evaluate_all.py
│   │
│   ├── utils/
│   │   ├── dl_models.py
│   │   ├── dl_tokenizers.py
│   │   ├── data_utils.py
│   │   ├── metrics_utils.py
│   │   └── url_features.py
│   │
│   └── requirements.txt
│
├── public/
│
├── src/
│   ├── api/
│   │   └── client.js
│   │
│   ├── assets/
│   │
│   ├── components/
│   │   └── ui.js
│   │
│   ├── pages/
│   │   ├── landing.js
│   │   ├── about.js
│   │   ├── dashboard.js
│   │   ├── fakeNews.js
│   │   ├── fraud.js
│   │   ├── urlDetection.js
│   │   └── performance.js
│   │
│   ├── router/
│   │   └── router.js
│   │
│   ├── styles/
│   │
│   └── utils/
│
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
├── README.md
└── start.bat
```

---

# 🚀 Getting Started

Follow these steps to run CyberSentinel on your local computer.

## 1. Clone the Repository

```bash
git clone https://github.com/suryateja-3/CyberSentinel.git
```

## 2. Navigate to the Project

```bash
cd CyberSentinel
```

## 3. Install Frontend Dependencies

Make sure Node.js and npm are installed.

```bash
npm install
```

## 4. Configure Python Environment

Create a Python virtual environment for the ML pipeline.

```bash
cd ml-pipeline
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Return to the project root:

```bash
cd ..
```

## 5. Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env
```

Obtain an API key from:

[GNews API – https://gnews.io/](https://gnews.io/)

Add your API key to the `.env` file:

```env
GNEWS_API_KEY=your_actual_api_key
```

**Security Note:** Never upload your actual `.env` file or API credentials to GitHub.

## 6. Run CyberSentinel

Start both the backend and frontend using:

```bash
npm start
```

Alternatively, on Windows:

```bash
.\start.bat
```

### Run Components Separately

**Backend API:**

```bash
npm run api
```

**Frontend:**

```bash
npm run dev
```

Use the terminal output to identify the local frontend URL and backend API address.

---

# 🧪 Testing

CyberSentinel includes backend unit tests for API functionality and evidence retrieval.

### Run Evidence Service Tests

```bash
python -m unittest backend.tests.test_evidence_service
```

### Run Backend API Tests

```bash
python -m unittest backend.tests.test_api
```

### Run Fake News Advanced Tests

```bash
python -m unittest backend.tests.test_fake_news_advanced
```

The evidence service tests mock external API calls, allowing tests to run without consuming actual GNews API requests.

---

# 📊 Model Evaluation

CyberSentinel includes evaluation reports for its three deep learning models.

| Model      | Application             | Evaluation Report                  |
| ---------- | ----------------------- | ---------------------------------- |
| DistilBERT | Fake News Detection     | `fake_news_distilbert_metrics.txt` |
| LSTM       | Fraud SMS Detection     | `fraud_lstm_metrics.txt`           |
| 1D CNN     | Malicious URL Detection | `url_cnn_metrics.txt`              |

Additional independent fake news evaluation results are available in:

```text
ml-pipeline/reports/
```

---

# 📸 Screenshots

Add actual application screenshots here to demonstrate the working interface.

| Module                   | Screenshot     |
| ------------------------ | -------------- |
| 🏠 Home Page             | Add screenshot |
| 📰 Fake News Detection   | Add screenshot |
| 📩 Fraud Detection       | Add screenshot |
| 🔗 URL Detection         | Add screenshot |
| 📊 Performance Dashboard | Add screenshot |

---

# 🔮 Future Enhancements

- 🤖 Advanced AI-based threat detection.
- 🌍 Multilingual fake news detection.
- 📈 Improved model accuracy and evaluation.
- 🔍 Enhanced real-time evidence verification.
- 📱 Mobile-friendly cybersecurity application.
- 🛡️ Advanced phishing and fraud detection.
- 📊 Detailed threat analytics and reporting.
- ⚡ Optimized model inference and performance.

---

# 💡 Why CyberSentinel?

Traditional cybersecurity tools often focus on detecting only one type of threat.

**CyberSentinel brings three important detection capabilities into one platform: Fake News Detection, Online Fraud Detection, and Malicious URL Detection.**

By combining DistilBERT, LSTM, and 1D CNN architectures with real-world news evidence retrieval, the platform provides a unified approach to analyzing suspicious digital content.

It demonstrates how Artificial Intelligence and Deep Learning can be applied to practical cybersecurity challenges.

---

# ⭐ Support

If you find CyberSentinel useful:

- ⭐ Star this repository.
- 🍴 Fork the project.
- 🐛 Report issues and bugs.
- 💡 Suggest improvements.
- 🤝 Contribute to future development.

---

<p align="center">
  <strong>🛡️ CyberSentinel</strong>
  <br>
  <em>Detecting Digital Threats with Artificial Intelligence</em>
  <br><br>
  Made with ❤️ using Python, PyTorch, Flask, JavaScript and Deep Learning.
</p>
