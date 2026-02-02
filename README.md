# AIssential Legal Agent

Automated contract analysis agent that monitors Google Drive for new contracts, analyzes them using Claude AI, and sends Telegram alerts for high-risk documents.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Features

- **Automatic Contract Analysis** - Monitors a Google Drive folder for new contract uploads
- **AI-Powered Risk Scoring** - Uses Claude API to analyze contracts and assign a risk score (0-100)
- **Telegram Alerts** - Instant notifications for high-risk contracts requiring attention
- **Multi-Format Support** - Handles both PDF and DOCX document formats
- **Duplicate Prevention** - Tracks processed files to avoid reprocessing the same document

---

## Architecture

```
+----------------+     +-------------------+     +-------------+     +----------+
|                |     |                   |     |             |     |          |
|  Google Drive  +---->+  Legal Agent      +---->+  Claude API +---->+ Telegram |
|  (Contracts)   |     |  (Python App)     |     |  (Analysis) |     | (Alerts) |
|                |     |                   |     |             |     |          |
+----------------+     +-------------------+     +-------------+     +----------+
                              |
                              v
                       +-------------+
                       | Processed   |
                       | Files Log   |
                       +-------------+
```

---

## Prerequisites

| Requirement | Description |
|-------------|-------------|
| **Python 3.10+** | Required runtime environment |
| **Google Cloud Service Account** | With Drive API enabled and credentials JSON file |
| **Telegram Bot** | Created via [@BotFather](https://t.me/BotFather) with token and chat ID |
| **Anthropic API Key** | For Claude AI contract analysis |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/aissential-legal-agent.git
cd aissential-legal-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials (see Configuration section below).

### 5. Set up Google Cloud credentials

Place your Google Cloud service account JSON file in the project directory and reference it in `.env`.

---

## Configuration

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CREDENTIALS_PATH` | Path to Google Cloud service account JSON | `./credentials.json` |
| `GOOGLE_DRIVE_FOLDER_ID` | ID of the Google Drive folder to monitor | `1ABC123def456GHI` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key for Claude | `sk-ant-...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | `123456789:ABC...` |
| `TELEGRAM_CHAT_ID` | Chat ID to receive alerts | `-1001234567890` |
| `RISK_THRESHOLD` | Minimum risk score to trigger alert (0-100) | `70` |
| `PROCESSED_FILES_PATH` | Path to store processed files log | `./processed_files.json` |

---

## Usage

### Manual Execution

Run the agent manually to scan for new contracts:

```bash
python app/main.py
```

### Automated Scanning with Cron

Set up a cron job to run the agent periodically:

```bash
# Edit crontab
crontab -e

# Run every 15 minutes
*/15 * * * * cd /path/to/aissential-legal-agent && /path/to/venv/bin/python app/main.py >> /var/log/legal-agent.log 2>&1
```

---

## Deployment on VPS (Ubuntu)

### 1. Connect to your VPS

```bash
ssh user@your-vps-ip
```

### 2. Install Python and dependencies

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip -y
```

### 3. Clone and set up the project

```bash
cd /opt
sudo git clone https://github.com/your-username/aissential-legal-agent.git
cd aissential-legal-agent
sudo python3.10 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
```

### 4. Configure environment

```bash
sudo cp .env.example .env
sudo nano .env  # Add your credentials
```

### 5. Upload Google credentials

```bash
# From your local machine
scp credentials.json user@your-vps-ip:/opt/aissential-legal-agent/
```

### 6. Set up cron job

```bash
sudo crontab -e
```

Add the following line to scan every 15 minutes:

```cron
*/15 * * * * cd /opt/aissential-legal-agent && /opt/aissential-legal-agent/venv/bin/python app/main.py >> /var/log/legal-agent.log 2>&1
```

### 7. Create log file

```bash
sudo touch /var/log/legal-agent.log
sudo chmod 666 /var/log/legal-agent.log
```

### 8. Test the deployment

```bash
cd /opt/aissential-legal-agent
./venv/bin/python app/main.py
```

---

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 AIssential

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
