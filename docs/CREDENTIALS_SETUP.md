# Credentials Setup Guide

This guide provides step-by-step instructions for setting up all required credentials for the Aissential Legal Agent.

---

## Table of Contents

1. [Anthropic API Key](#1-anthropic-api-key)
2. [Telegram Bot](#2-telegram-bot)
3. [Google Cloud Service Account](#3-google-cloud-service-account)
4. [Google Drive Folder](#4-google-drive-folder)
5. [Environment Variables Summary](#5-environment-variables-summary)

---

## 1. Anthropic API Key

The Anthropic API key is required to access Claude AI models for contract analysis.

### Steps

1. **Navigate to Anthropic Console**
   - Open your browser and go to [console.anthropic.com](https://console.anthropic.com)

2. **Create Account or Login**
   - If you don't have an account, click **Sign Up** and follow the registration process
   - If you already have an account, click **Log In** and enter your credentials

3. **Access API Keys Section**
   - Once logged in, navigate to **API Keys** in the left sidebar
   - Or go directly to [console.anthropic.com/account/keys](https://console.anthropic.com/account/keys)

4. **Create a New API Key**
   - Click the **Create Key** button
   - Give your key a descriptive name (e.g., "aissential-legal-agent")
   - Click **Create**

5. **Copy the API Key**
   - **Important**: The key will only be shown once. Copy it immediately.
   - Store it securely - you won't be able to see it again

6. **Add to Environment Variables**
   - Open your `.env` file in the project root
   - Add the following line:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   - Replace the placeholder with your actual API key

---

## 2. Telegram Bot

The Telegram bot is used to send notifications and alerts about contract analysis results.

### Steps

#### 2.1 Create the Bot

1. **Open Telegram**
   - Launch the Telegram app on your device (mobile or desktop)

2. **Find BotFather**
   - In the search bar, type `@BotFather`
   - Select the official BotFather account (look for the verified checkmark)

3. **Start a Conversation**
   - Click **Start** or send `/start` to begin

4. **Create a New Bot**
   - Send the command: `/newbot`

5. **Choose a Name**
   - BotFather will ask for a name for your bot
   - Enter a display name (e.g., "Aissential Legal Agent")

6. **Choose a Username**
   - Enter a unique username ending in `bot` (e.g., "aissential_legal_bot")
   - If the username is taken, try another one

7. **Save the Bot Token**
   - BotFather will provide an HTTP API token
   - It looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Copy this token

8. **Add to Environment Variables**
   - Open your `.env` file
   - Add the following line:
   ```
   TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   - Replace with your actual token

#### 2.2 Get Your Chat ID

1. **Send a Message to Your Bot**
   - In Telegram, search for your bot by its username
   - Click **Start** or send any message to the bot

2. **Get Updates via API**
   - Open a terminal or command prompt
   - Run the following command (replace `<TOKEN>` with your bot token):
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
   - On Windows PowerShell, use:
   ```powershell
   Invoke-RestMethod -Uri "https://api.telegram.org/bot<TOKEN>/getUpdates"
   ```

3. **Find the Chat ID**
   - Look for the `"chat"` object in the response
   - Find the `"id"` field - this is your Chat ID
   - Example response:
   ```json
   {
     "ok": true,
     "result": [{
       "message": {
         "chat": {
           "id": 123456789,
           "first_name": "Your Name",
           "type": "private"
         }
       }
     }]
   }
   ```

4. **Add to Environment Variables**
   - Open your `.env` file
   - Add the following line:
   ```
   TELEGRAM_CHAT_ID=123456789
   ```
   - Replace with your actual Chat ID

---

## 3. Google Cloud Service Account

A Google Cloud service account is required to access Google Drive API for reading contract files.

### Steps

#### 3.1 Create or Select a Project

1. **Navigate to Google Cloud Console**
   - Open your browser and go to [console.cloud.google.com](https://console.cloud.google.com)
   - Sign in with your Google account

2. **Create a New Project** (or select existing)
   - Click on the project dropdown at the top of the page
   - Click **New Project**
   - Enter a project name (e.g., "aissential-legal-agent")
   - Click **Create**
   - Wait for the project to be created and select it

#### 3.2 Enable Google Drive API

1. **Go to API Library**
   - In the left sidebar, navigate to **APIs & Services** > **Library**
   - Or go directly to [console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)

2. **Search for Google Drive API**
   - Type "Google Drive API" in the search bar
   - Click on **Google Drive API** in the results

3. **Enable the API**
   - Click the **Enable** button
   - Wait for the API to be enabled

#### 3.3 Create a Service Account

1. **Navigate to Service Accounts**
   - In the left sidebar, go to **IAM & Admin** > **Service Accounts**
   - Or go directly to [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts)

2. **Create Service Account**
   - Click **+ Create Service Account** at the top
   - Enter a service account name (e.g., "legal-agent-drive-access")
   - The service account ID will be auto-generated
   - Add a description (optional): "Service account for Aissential Legal Agent to access Google Drive"
   - Click **Create and Continue**

3. **Grant Roles** (optional for Drive access via sharing)
   - You can skip this step by clicking **Continue**
   - The service account will access Drive via folder sharing, not project-level permissions

4. **Complete Creation**
   - Click **Done** to finish creating the service account

#### 3.4 Create and Download JSON Key

1. **Open Service Account Details**
   - Click on the service account you just created

2. **Navigate to Keys Tab**
   - Click on the **Keys** tab

3. **Create New Key**
   - Click **Add Key** > **Create new key**
   - Select **JSON** as the key type
   - Click **Create**

4. **Download the Key**
   - The JSON key file will be automatically downloaded
   - Rename it to `gcp.json` for consistency

5. **Move Key to Secure Location**
   - Move the file to your application directory:
   ```bash
   # Linux/Mac
   mv ~/Downloads/your-project-xxxxxx.json /opt/aissential-legal-agent/gcp.json

   # Windows
   move %USERPROFILE%\Downloads\your-project-xxxxxx.json C:\opt\aissential-legal-agent\gcp.json
   ```
   - **Important**: Keep this file secure and never commit it to version control

6. **Note the Service Account Email**
   - The service account email looks like: `legal-agent-drive-access@your-project.iam.gserviceaccount.com`
   - You will need this email to share the Google Drive folder

---

## 4. Google Drive Folder

Set up a Google Drive folder to store contracts that the agent will analyze.

### Steps

#### 4.1 Create the Contracts Folder

1. **Open Google Drive**
   - Go to [drive.google.com](https://drive.google.com)
   - Sign in with your Google account

2. **Create a New Folder**
   - Click **+ New** > **Folder**
   - Name the folder (e.g., "Legal Contracts" or "Aissential Contracts")
   - Click **Create**

#### 4.2 Get the Folder ID

1. **Open the Folder**
   - Double-click on the folder you just created

2. **Copy the Folder ID from URL**
   - Look at your browser's address bar
   - The URL will look like: `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz`
   - The folder ID is the string after `/folders/`: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

3. **Add to Environment Variables**
   - Open your `.env` file
   - Add the following line:
   ```
   GOOGLE_DRIVE_FOLDER_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
   ```
   - Replace with your actual folder ID

#### 4.3 Share Folder with Service Account

1. **Right-Click the Folder**
   - In Google Drive, right-click on your contracts folder
   - Select **Share** > **Share**

2. **Add Service Account Email**
   - In the "Add people and groups" field, paste the service account email
   - Example: `legal-agent-drive-access@your-project.iam.gserviceaccount.com`

3. **Set Permissions**
   - Select **Viewer** from the dropdown (read-only access is sufficient)
   - Uncheck "Notify people" (service accounts don't have email)

4. **Share**
   - Click **Share** to confirm

---

## 5. Environment Variables Summary

After completing all the steps above, your `.env` file should contain the following variables:

```env
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key-here

# Telegram Bot
TELEGRAM_TOKEN=1234567890:your-telegram-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=your-folder-id-here
```

### File Locations

| File | Location | Description |
|------|----------|-------------|
| `.env` | Project root | Environment variables |
| `gcp.json` | `/opt/aissential-legal-agent/gcp.json` | Google Cloud service account key |

### Security Reminders

- **Never commit** `.env` or `gcp.json` to version control
- Add both files to your `.gitignore`:
  ```
  .env
  gcp.json
  *.json
  ```
- Keep backup copies of your credentials in a secure password manager
- Rotate API keys periodically for security
- Use the principle of least privilege - only grant necessary permissions

---

## Troubleshooting

### Anthropic API Key Issues

- **401 Unauthorized**: Verify the API key is correctly copied without extra spaces
- **Rate limits**: Check your Anthropic console for usage limits

### Telegram Bot Issues

- **No updates returned**: Make sure you sent a message to the bot first
- **Invalid token**: Verify the token is correctly copied from BotFather
- **Chat ID not found**: Send another message and try the getUpdates call again

### Google Drive Issues

- **403 Forbidden**: Verify the folder is shared with the service account email
- **404 Not Found**: Check that the folder ID is correct
- **Invalid credentials**: Ensure gcp.json is valid and in the correct location

---

## Next Steps

After setting up all credentials:

1. Verify your `.env` file contains all required variables
2. Verify `gcp.json` is in place at `/opt/aissential-legal-agent/gcp.json`
3. Run the application's credential verification command (if available)
4. Upload a test contract to your Google Drive folder
5. Run the agent to verify everything works correctly
