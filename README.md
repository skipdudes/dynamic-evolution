# Dynamic Evolution
todo

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
