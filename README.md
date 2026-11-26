# CyberSentinel (Secure Net Project)

CyberSentinel is an AI-powered cybersecurity platform for detecting Fake News, Online Fraud, and Malicious URLs.

## Project Structure
- `src/`: Vanilla JavaScript frontend (Vite).
- `ml-pipeline/`: Reproducible machine learning training scripts and datasets.
- `backend/`: Flask REST API serving ML predictions and Evidence Retrieval.

## Quick Start (Running the Application)

To run both the Python Flask Backend and the Web Frontend together:

```bash
npm start
```
*(or run `.\start.bat` on Windows)*

Alternatively, run them separately in two terminals:
- **Backend API**: `npm run api` (or `.\ml-pipeline\.venv\Scripts\python.exe backend/app.py`)
- **Frontend**: `npm run dev`

> **Note**: When you close your laptop or sleep Windows, background terminal processes terminate. Make sure to restart with `npm start` when reopening your project.


## Stage 3: News Evidence Retrieval Module

To bolster our ML predictions, CyberSentinel includes an Evidence Retrieval module that searches real-world news reports (via GNews) to find corroborating or contradicting evidence for a given claim.

### Security Precautions & Configuration
**Never hardcode API keys in the frontend JavaScript or commit them to Git.**
We use environment variables in a `.env` file that is parsed securely by the backend and ignored by `.gitignore`.

1. Copy the `.env.example` file to create your local `.env`:
   ```bash
   cp .env.example .env
   ```
2. Obtain a free GNews API key from [https://gnews.io/](https://gnews.io/).
3. Paste the key into your `.env` file:
   ```env
   GNEWS_API_KEY=your_actual_api_key
   ```

### Architecture Overview

The Fake News Detection page now runs two processes in parallel:

1. **DL Prediction** (`POST /api/detect/fake-news`): 
   - A PyTorch-based DistilBERT contextual classification.
2. **Evidence Verification** (`POST /api/verify/evidence`):
   - Calls the backend `evidence_service.py`.
   - The backend securely queries the GNews API.
   - Evaluates excerpts for supporting or contradicting language.
   - Returns related articles and an NLI-style verdict (Supporting, Contradicting, Mixed, Insufficient).

*Note: We never assert a claim is definitively true or false solely based on the presence of a search result. The Deep Learning models and the verification service remain strictly separated.*

## Testing

The backend includes unit tests that mock the external API calls. This ensures CI pipelines and local testing do not exhaust API rate limits or require actual credentials.

```bash
python -m unittest backend.tests.test_evidence_service
```
