# LegalLens – Risk-Aware Terms Analyzer

LegalLens is a privacy-first, risk-aware legal document analyzer that uses a novel risk propagation engine to identify, quantify, and visualize liabilities in complex contracts.

## 🚀 System Architecture

### Pipeline Overview
1.  **Input Layer**:
    *   Chrome Extension (Manifest V3) for real-time web analysis.
    *   Web Dashboard for document upload (.pdf, .txt).
2.  **Preprocessing**:
    *   Clause Segmentation: Heuristic + NLP splitting.
    *   Embedding Layer: `distilbert-base-uncased` (Singleton, FP16 optimized).
3.  **Risk Analysis Core (The Patentable Engine)**:
    *   **Base Risk Scoring**: Keyword + Zero-shot classification.
    *   **Dependency Graph**: NetworkX graph where Nodes=Clauses, Edges=Semantic Similarity.
    *   **Risk Propagation**: Recursive algorithm diffusing risk from high-liability nodes to dependent clauses.
    *   **Personalization**: Weighting based on user sensitivity profile.
4.  **Output Layer**:
    *   Interactive Heatmap & Force-Directed Graph.
    *   Risk-Prioritized Summarization (DistilBART).
    *   Explainability (Attention-based token highlighting).

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js & npm
- CUDA-capable GPU (Optional, auto-fallback to CPU)

### 1. Backend Setup
```bash
cd legal_lens
# Run the setup script (Windows)
setup_env.bat
# Or manually:
# python -m venv venv
# venv\Scripts\activate
# pip install -r requirements.txt

# Start the API
cd legal_lens
# Ensure venv is active
# venv\Scripts\activate
uvicorn backend.main:app --reload
```
*API runs at http://localhost:8000*

### 2. Frontend Setup
```bash
cd legal_lens/frontend
npm install
npm run dev
```
*Dashboard runs at http://localhost:5173*

### 3. Chrome Extension Setup
1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer mode** (top right).
3.  Click **Load unpacked**.
4.  Select the `legal_lens/extension` directory.
5.  Pin the extension and visit any Terms & Conditions page to analyze.

---
