# 🛡️ SafeChat — AI-Powered Content Moderation System

A desktop application that uses BERT-based deep learning to detect toxic, offensive, and harmful content in real time.

Built with **HuggingFace Transformers**, **PyTorch**, and **CustomTkinter**.

---

## 📸 Demo

![SafeChat UI](assets/demo.png)

---

## 🧠 How It Works

SafeChat uses [`unitary/toxic-bert`](https://huggingface.co/unitary/toxic-bert) — a DistilBERT model fine-tuned on the **Jigsaw Toxic Comment Classification** dataset from Kaggle.

The model classifies any input message across **6 toxicity categories** simultaneously:

| Category | Description |
|---|---|
| `toxic` | General toxicity |
| `severe_toxic` | Highly offensive content |
| `obscene` | Explicit / obscene language |
| `threat` | Threatening language |
| `insult` | Personal insults |
| `identity_hate` | Hate speech targeting identity groups |

Each category returns a **confidence score (0–1)**. A message is flagged as toxic if any category exceeds **0.5**.

---

## 🚀 Features

- ✅ Real-time toxicity classification using BERT
- ✅ 6-category breakdown with confidence scores
- ✅ Visual toxicity score bar
- ✅ Recent analysis history panel
- ✅ Clean dark-themed CustomTkinter GUI
- ✅ Runs fully offline after first model download
- ✅ CPU-friendly (no GPU required)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | CustomTkinter |
| Model | unitary/toxic-bert (HuggingFace) |
| Framework | PyTorch + Transformers |
| Language | Python 3.11 |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/akshay-2005-13/SafeChat.git
cd SafeChat
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

> ⚠️ **First run:** The model (~250MB) will be downloaded automatically from HuggingFace. This is a one-time download. After that, it runs fully offline.

---

## 📁 Project Structure

```
SafeChat/
├── app.py              # Main CustomTkinter UI application
├── model.py            # ToxicityClassifier class (BERT wrapper)
├── requirements.txt    # Python dependencies
├── assets/
│   └── demo.png        # UI screenshot
└── README.md
```

---

## 🧪 Testing the Model Directly

You can test the classifier independently without the GUI:

```bash
python model.py
```

This runs 5 sample messages through the classifier and prints results to the terminal.

---

## 📊 Model Details

| Property | Value |
|---|---|
| Base Model | DistilBERT |
| Fine-tuned on | Jigsaw Toxic Comment Dataset |
| HuggingFace ID | `unitary/toxic-bert` |
| Input Max Length | 512 tokens |
| Output | Multi-label sigmoid scores |
| Threshold | 0.5 per category |

---

## 🔮 Future Improvements

- [ ] Batch message analysis from CSV/TXT files
- [ ] REST API with Flask for web integration
- [ ] Export analysis reports to PDF
- [ ] Multi-language support
- [ ] Custom threshold configuration

---

## 👨‍💻 Author

**Vootkuri Akshay Reddy**
- GitHub: [@akshay-2005-13](https://github.com/akshay-2005-13)
- LinkedIn: [vootkuri-akshay-reddy](https://linkedin.com/in/vootkuri-akshay-reddy)

---

## 📄 License

MIT License — free to use, modify, and distribute.
