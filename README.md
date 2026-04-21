# Trilium MCP Server for Gemini CLI

This project provides a Model Context Protocol (MCP) server, a specialized Gemini Skill, and an autonomous Agent for managing [Trilium Notes](https://github.com/zadam/trilium) directly from your terminal using the [Gemini CLI](https://github.com/google/gemini-cli).

## Features

- **Full ETAPI Integration**: Create, search, move, and edit notes using natural language.
- **Autonomous Agent**: A dedicated `trilium-assistant` agent for complex organizational tasks.
- **Specialized Skill**: Expert guidance on Trilium's note tree structure and attributes.
- **Secure**: Uses a `.env` file to protect your API tokens.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- **Python 3.10+**
- **Node.js** (for Gemini CLI)
- **Trilium Notes** (with ETAPI enabled)

### 2. Clone the Repository
```bash
git clone https://github.com/dhiraj-ydv/trilium-mcp.git
cd trilium-mcp
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your Trilium details:
```bash
cp .env.example .env
```
Open `.env` and provide:
- `TRILIUM_SERVER_URL`: Your Trilium instance URL (e.g., `http://localhost:8080`).
- `TRILIUM_ETAPI_TOKEN`: Your ETAPI token (generated in Trilium Settings > Options > ETAPI).

---

## 🚀 Usage with Gemini CLI

### Initialization
Simply run `gemini` inside the project directory. The CLI will automatically discover the MCP server, Agent, and Skill defined in the `.gemini/` folder.

### Commands

#### Using the Autonomous Agent
The agent can handle multi-step tasks like finding a note and moving it:
> `@trilium-assistant move my 'Drafts' note into the 'Projects' folder.`

#### Using Direct MCP Tools
Perform surgical actions directly:
> `mcp_trilium-mcp_create_note title="Meeting Notes" parentNoteId="root" content="Hello World"`

#### Activating the Skill
Get expert advice on how to structure your notes:
> `activate_skill trilium-notes`

---

## 📂 Project Structure

- `server.py`: The MCP server implementation.
- `.gemini/settings.json`: Configuration for the Gemini CLI to load the server.
- `.gemini/agents/trilium-assistant.md`: The autonomous agent definition.
- `.gemini/skills/trilium-notes/`: Specialized knowledge for Trilium workflows.

## 🛡️ Security
This project uses a `.gitignore` to ensure your `.env` file is never pushed to GitHub. **Never share your `.env` file or ETAPI token.**

## 📄 License
MIT
