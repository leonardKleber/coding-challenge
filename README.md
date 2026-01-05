# HubSpot Contact–Company Association Script

This script creates a contact and a company in HubSpot and links the contact to the company with an **Employee** association.

---

## Prerequisites

- Python **3.10+**
- A HubSpot **Private App access token**
- Internet access

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/leonardKleber/coding-challenge
cd coding-challenge
```

### 2. Create and activate a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate        # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file
```bash
HUBSPOT_KEY=your_hubspot_private_app_token_here
```

---

## Running the script
Once dependencies are installed and the `.env` file is set up, run:
```bash
python main.py
```
