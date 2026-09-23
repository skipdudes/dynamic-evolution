<p align="center">
  <a href="https://github.com/skipdudes/dynamic-evolution">
    <img src="docs/assets/logo.png" alt="Shadows of the Crown II" />
  </a>
</p>
<p align="center"><i>An LLM-powered 2D RPG where every conversation shapes the fate of the kingdom...</i></p>

**Shadows of the Crown II** returns you to a medieval world teetering on the brink of rebellion. Sent by the King to the restless province of Tarnstead, you must navigate a dangerous web of conspiracies, interacting with powerful mages, cunning smugglers, and weary tavern keepers. This game is a direct sequel to [**Shadows of the Crown**](https://github.com/skipdudes/adventure-game) and assumes that the player remained loyal to the King.

<p align="center">
  <a href="https://www.youtube.com/watch?v=9dFmNVkm_lo">
    <img src="docs/assets/gameplay.gif" alt="Gameplay GIF" />
  </a>
</p>
<p align="center"><i>Click on the gameplay GIF to watch the whole gameplay.</i></p>

---

This repository contains the source code for **Shadows of the Crown II** (repo name: [`dynamic-evolution`](https://github.com/skipdudes/dynamic-evolution)).

## 🛠 Requirements
- Python 3.10+
- pip
> All required Python packages are listed in [`requirements.txt`](requirements.txt).
> To enable dialogue generation, you must **generate your own** [**Groq API key**](https://console.groq.com/keys).

## ⚙️ Setup
### 1️⃣ Clone the repository
```bash
git clone https://github.com/skipdudes/dynamic-evolution.git
cd dynamic-evolution
```
### 2️⃣ Create a virtual environment
```
python -m venv .venv
```
### 3️⃣ Activate the virtual environment
#### 🪟 Windows
```bash
.venv\Scripts\activate
```
#### 🐧 Linux / 🍎 macOS
```bash
source .venv/bin/activate
```
### 4️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
### 5️⃣ Create an `.env` file in the project root
```markdown
GROQ_API_KEY=your_api_key_here
```
Replace `your_api_key_here` with your personal [**Groq API key**](https://console.groq.com/keys).

## ▶ Running
Run the main script:
```bash
python main.py
```

## 📜 License
This project is licensed under the [MIT](LICENSE) license.

## 🎨 Credits
todo

## 👤 Author
Copyright &copy; 2026 Marcin Chętnik
