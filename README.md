# 📝 Docs MCP Server

Welcome to the **Docs MCP Server**!  
This tool gives your AI the ability to create and edit Google Docs via MCP, turning natural language into powerful document workflows.

So you can do things like this:

<img width="1239" alt="Screenshot 2025-06-07 at 4 20 06 PM" src="https://github.com/user-attachments/assets/ce7b0c75-4864-4401-86ce-c0c09bc60a2c" />

---

## ⚙️ Core Functionalities

With this server, your AI (like Claude or GPT) can:

✅ Create a new Google Doc with just a title  
✅ Create a new Google Doc with both title and content  
✅ Add more content to an existing document  
✅ Create google calendar events & list out the next x events with just plain text


---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/docs-mcp-server.git
cd docs-mcp-server
```

### 2. Install MCP CLI

```bash
uv add "mcp[cli]"
```

### 3. Create & Activate a Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```


### 5. Set Up Google Docs API

- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Enable the **Google Docs API**.
- Create OAuth credentials and **choose "Desktop Application"** when asked for the app type.
- Download the `credentials.json` file.
- Place the file in your project folder.
- In `authentication.py`, set the `CREDENTIALS_PATH` to the path of your `credentials.json`.

<img width="1059" alt="Screenshot 2025-06-07 at 4 23 08 PM" src="https://github.com/user-attachments/assets/6eebf3d1-3cab-445c-aa2e-17c9e9d82e98" />

### 6. Run the Server

```bash
python server.py
```


- This will open a Google OAuth window in your browser.
- Once authenticated, a `token.pickle` file will be generated.
- In `authentication.py`, set the `TOKEN_FILE` to the path of your `token.pickle`.

<img width="1373" alt="Screenshot 2025-06-07 at 4 24 30 PM" src="https://github.com/user-attachments/assets/8831bdd9-1a8b-4306-8dbc-8d25d8a7c390" />

🎉 Your Docs MCP server is now running!

---

## 🧠 Connecting to Claude (Anthropic)

1. **Ensure Claude Desktop is Installed**

2. Run the MCP server install command:

```bash
mcp install server.py
```

3. Open **Claude Desktop App Settings**  
   (Cmd + `,` or click on the Cluade button in the top bar, and navigate to settings)

<img width="1440" alt="Screenshot 2025-06-07 at 4 16 02 PM" src="https://github.com/user-attachments/assets/2bf2dcd8-3b67-4be1-bf66-2e6b139e73ad" />

4. Navigate to the **Developer** tab  
   You should see `google-docs-mcp` listed.


> ⚠️ If you see errors, don’t worry — continue below.

5. Click **"Edit Config"** at the bottom left. This opens your `claude_desktop_config.json`.

<img width="1440" alt="Screenshot 2025-06-07 at 4 17 15 PM" src="https://github.com/user-attachments/assets/69148870-c928-465c-b0fa-75dc2f23f1c4" />

   

7. Locate your `google-docs-mcp` entry. Update the `args` to include necessary dependencies:

### 🔧 Before:
```json
"args": [
  "run",
  "--with",
  "mcp[cli]",
  "mcp",
  "run",
  "$YOUR PATH"
]
```

### ✅ After:
```json
"google-docs-mcp": {
  "command": "/usr/local/bin",  // or wherever your Python binaries live
  "args": [
    "run",
    "--with",
    "mcp[cli]",
    "--with",
    "google-api-python-client",
    "--with",
    "google-auth",
    "--with",
    "google-auth-oauthlib",
    "--with",
    "google-auth-httplib2",
    "--with",
    "python-dotenv",
    "mcp",
    "run",
    "/Users/sujannandikolsunilkumar/docs mcp/docs-mcp/server.py" #Your path will be different, don't need to change it. 
  ]
}
```



7. Save the file and **restart Claude Desktop**.

---

## ✅ Final Test

After restarting Claude:

- You should be prompted to complete Google OAuth.
- Once authorized, click on **"Search & Tools"** inside Claude.
  
  <img width="1055" alt="Screenshot 2025-06-07 at 4 22 00 PM" src="https://github.com/user-attachments/assets/eb0ceb79-1ecd-4abc-8975-9a8654c367c4" />

- You should see your **Google Docs MCP Server** listed and ready.
  <img width="714" alt="Screenshot 2025-06-07 at 3 52 17 PM" src="https://github.com/user-attachments/assets/c0b80230-53d0-4d5c-a9da-4b79d300a51b" />

---

## ✨ You Can Now Ask Claude To:

- Create a Google Doc and give it a title  
- Create a Google Doc with 
a title and content  
- Add more text to an existing Google Doc

<img width="1239" alt="Screenshot 2025-06-07 at 4 20 06 PM" src="https://github.com/user-attachments/assets/ce7b0c75-4864-4401-86ce-c0c09bc60a2c" />
---

## 🆘 Need Help?

Feel free to reach out:  
📧 **nandikolsujan@gmail.com**

---

## 🧠 About MCP

This project uses **Model Context Protocol (MCP)** to enable LLMs to interact with tools directly through self-describing interfaces—no hardcoding needed. Claude reads and understands the tool capabilities and executes accordingly.

---
