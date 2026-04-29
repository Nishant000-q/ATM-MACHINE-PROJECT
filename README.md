# ATM Project — Setup & Run Guide

## Folder structure
```
atm/
├── app.py            ← Flask backend
├── index.html        ← Frontend (HTML/CSS/JS)
├── customers.json    ← Your data file
├── requirements.txt
└── README.md
```

## Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

## Step 2 — Run the Flask server
```bash
python app.py
```
Server starts at: http://127.0.0.1:5000

## Step 3 — Open the frontend
Open `index.html` directly in your browser.
Or visit http://127.0.0.1:5000 (Flask also serves it).

---

## Test accounts (in customers.json)
| Account ID | PIN  | Name          | Balance   |
|------------|------|---------------|-----------|
| ACC001     | 1234 | Rahul Sharma  | ₹50,000   |
| ACC002     | 5678 | Priya Mehta   | ₹1,20,000 |
| ACC003     | 9999 | Arjun Singh   | ₹8,500    |

---

## API Endpoints
| Method | Route               | What it does         |
|--------|---------------------|----------------------|
| POST   | /api/login          | Authenticate user    |
| POST   | /api/balance        | Get current balance  |
| POST   | /api/deposit        | Add money            |
| POST   | /api/withdraw       | Withdraw money       |
| POST   | /api/transfer       | Transfer to another  |
| POST   | /api/transactions   | Last 10 transactions |

All endpoints accept and return JSON.
