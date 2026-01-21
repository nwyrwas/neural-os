# NeuralOS

An AI-powered notes application that understands the meaning behind your notes, not just keywords. Search and recall your thoughts using natural language, powered by semantic search and GPT-4.

🔗 **Live Demo**: Coming Soon
📂 **GitHub**: [github.com/nwyrwas/neural-os](https://github.com/nwyrwas/neural-os)

---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running Locally](#running-locally)
- [Project Structure](#project-structure)
- [Technical Deep Dive](#technical-deep-dive)
  - [Semantic Search with Vector Embeddings](#semantic-search-with-vector-embeddings)
  - [RAG Pipeline Implementation](#rag-pipeline-implementation)
  - [Authentication Flow](#authentication-flow)
- [API Documentation](#api-documentation)
- [Challenges & Solutions](#challenges--solutions)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

NeuralOS is a full-stack AI-powered notes application that allows you to capture, organize, and recall your thoughts using natural language. Unlike traditional note-taking apps that rely on keyword matching, NeuralOS understands the **meaning** behind your notes through semantic search powered by OpenAI embeddings and Pinecone vector database.

Ask questions like *"What did I write about machine learning projects?"* and NeuralOS will find relevant notes even if they don't contain those exact words.

### Why I Built This

As a software engineering student and developer, I wanted to build a project that:
- Demonstrates full-stack development capabilities (React frontend + FastAPI backend)
- Showcases AI/ML integration with production-ready APIs (OpenAI, Pinecone)
- Implements modern authentication patterns (OAuth + email/password)
- Solves a real problem I personally experience with note-taking

---

## Preview

![Neural OS Preview 1](./frontend/public/neural-os-1.jpg)
![Neural OS Preview 2](./frontend/public/neural-os-2.jpg)

## Problem Statement

Traditional note-taking apps have a critical flaw: **finding your notes later is painful**.

- **Keyword search fails** when you can't remember the exact words you used
- **Folders and tags** require upfront organization that breaks your flow
- **No context awareness** means searching is limited to exact text matches

**NeuralOS solves this** by understanding the semantic meaning of your notes, allowing you to search by concept rather than keywords.

---

## Key Features

### 🧠 AI-Powered Semantic Search
- Search notes by meaning, not just keywords
- Powered by OpenAI text-embedding-3-small for vector embeddings
- Pinecone vector database for fast similarity search
- Related notes suggestions with match percentages

### 💬 GPT-4 Contextual Answers
- Ask questions in natural language
- GPT-4o-mini synthesizes answers from your entire knowledge base
- Retrieval-Augmented Generation (RAG) pipeline for context-aware responses
- Cites relevant notes used to generate answers

### 🔐 Multi-Provider Authentication
- Email/password authentication
- Google OAuth sign-in
- GitHub OAuth sign-in
- Powered by Supabase Auth

### 📝 Full Note Management
- Create, edit, and delete notes
- Rich text support with Markdown rendering
- Auto-save functionality
- Favorites and Archive organization
- Trash & Restore with 30-day retention

### 🎨 Modern User Experience
- Dark mode and light mode
- Keyboard shortcuts for power users
- Responsive design (mobile, tablet, desktop)
- Real-time search results
- Clean, minimal interface

---

## Tech Stack

### Frontend
- **React 19** - Component-based UI library
- **Create React App** - Build tooling and development server
- **Axios** - HTTP client for API requests
- **React Markdown** - Markdown rendering for notes
- **Lucide React** - Icon library
- **CSS3** - Custom styling with CSS variables for theming

### Backend
- **FastAPI** - Modern Python web framework with async support
- **Python 3.11** - Programming language
- **Uvicorn** - ASGI server for FastAPI

### AI & Machine Learning
- **OpenAI API**
  - `text-embedding-3-small` - Vector embeddings for semantic search
  - `gpt-4o-mini` - Chat completions for contextual answers
- **Pinecone** - Vector database for similarity search
- **RAG Pipeline** - Retrieval-Augmented Generation for context-aware AI

### Database & Auth
- **Supabase** - Backend-as-a-Service
  - PostgreSQL database for note storage
  - User authentication (email, Google, GitHub OAuth)
  - Row-level security (RLS) policies

### DevOps & Tools
- **Git/GitHub** - Version control
- **npm** - Frontend package management
- **pip** - Backend package management
- **Environment Variables** - Configuration management
- **CORS** - Cross-origin resource sharing

---

## Architecture

NeuralOS follows a **client-server architecture** with clear separation of concerns:

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│                 │         │                  │         │                 │
│  React Frontend │◄───────►│  FastAPI Backend │◄───────►│  Supabase DB    │
│  (Port 3000)    │   REST  │  (Port 8000)     │         │  (PostgreSQL)   │
│                 │   API   │                  │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                    │
                                    │
                                    ▼
                            ┌───────────────────┐
                            │                   │
                            │   AI Services     │
                            │                   │
                            │  • OpenAI API     │
                            │  • Pinecone       │
                            │                   │
                            └───────────────────┘
```

### Data Flow

1. **User creates/edits a note** → Saved to Supabase PostgreSQL
2. **Auto-indexing** → Note content sent to OpenAI for embedding generation
3. **Vector storage** → Embedding stored in Pinecone with metadata
4. **User searches** → Query embedded → Pinecone similarity search → Results returned
5. **User asks question** → RAG pipeline retrieves relevant notes → GPT-4 generates answer

---

## Getting Started

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+** and pip
- **Supabase Account** (free tier available)
- **OpenAI API Key** (paid, but embeddings are cheap)
- **Pinecone Account** (free tier available)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/nwyrwas/neural-os.git
cd neural-os
```

**2. Install frontend dependencies**
```bash
npm install
```

**3. Install backend dependencies**
```bash
cd backend  # or wherever your Python backend lives
pip install -r requirements.txt
```

### Environment Variables

**Frontend (.env in root directory)**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=your_supabase_project_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Backend (.env in backend directory)**
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

### Running Locally

**1. Start the backend server**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**2. Start the frontend development server** (in a separate terminal)
```bash
npm start
```

**3. Open your browser**
Navigate to [http://localhost:3000](http://localhost:3000)

---

## Project Structure

```
neural-os/
├── public/                     # Static assets
├── src/                        # React frontend source code
│   ├── components/            # React components
│   ├── App.js                 # Main application component
│   ├── App.css                # Application styles
│   └── index.js               # Entry point
├── backend/                    # FastAPI backend
│   ├── main.py                # FastAPI application and routes
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend environment variables
├── package.json               # Frontend dependencies
├── .env                       # Frontend environment variables
└── README.md                  # This file
```

---

## Technical Deep Dive

### Semantic Search with Vector Embeddings

Traditional keyword search matches exact words. Semantic search understands **meaning**.

**How it works:**

1. **Indexing Phase** (when you save a note):
   ```python
   # Convert note text to a vector embedding
   embedding = openai.Embedding.create(
       model="text-embedding-3-small",
       input=note_content
   )

   # Store in Pinecone with metadata
   pinecone_index.upsert([
       (note_id, embedding, {"user_id": user_id, "content": content})
   ])
   ```

2. **Search Phase** (when you search):
   ```python
   # Convert search query to embedding
   query_embedding = openai.Embedding.create(
       model="text-embedding-3-small",
       input=search_query
   )

   # Find similar vectors in Pinecone
   results = pinecone_index.query(
       vector=query_embedding,
       top_k=10,
       filter={"user_id": user_id}
   )
   ```

This allows searches like "machine learning projects" to find notes about "neural networks" or "deep learning" even without exact keyword matches.

### RAG Pipeline Implementation

Retrieval-Augmented Generation (RAG) gives GPT-4 context from your notes.

**Pipeline Flow:**

```
User Question
     ↓
[1] Embed question with OpenAI
     ↓
[2] Query Pinecone for similar notes (top 5)
     ↓
[3] Retrieve full note content from Supabase
     ↓
[4] Construct prompt with context
     ↓
[5] Send to GPT-4o-mini
     ↓
[6] Return synthesized answer with sources
```

**Example Prompt Construction:**
```python
context = "\n\n".join([note.content for note in retrieved_notes])

prompt = f"""You are a helpful assistant that answers questions based on the user's notes.

Context from notes:
{context}

User question: {user_question}

Provide a clear answer based on the context above. If the context doesn't contain relevant information, say so."""

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
```

### Authentication Flow

Supabase handles all authentication complexity:

**Email/Password Sign-up:**
```javascript
const { user, error } = await supabase.auth.signUp({
  email: email,
  password: password
})
```

**OAuth (Google/GitHub):**
```javascript
const { user, error } = await supabase.auth.signInWithOAuth({
  provider: 'google' // or 'github'
})
```

**Session Management:**
```javascript
// Check if user is authenticated
const session = supabase.auth.session()

// Listen for auth changes
supabase.auth.onAuthStateChange((event, session) => {
  // Update UI based on auth state
})
```

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### **POST /notes**
Create a new note and auto-index for search.

**Request:**
```json
{
  "user_id": "string",
  "title": "string",
  "content": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "string",
  "title": "string",
  "content": "string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### **GET /notes**
Get all notes for authenticated user.

**Query Parameters:**
- `user_id` (required): User ID from Supabase auth

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "string",
    "content": "string",
    "created_at": "timestamp"
  }
]
```

#### **GET /search**
Semantic search across user's notes.

**Query Parameters:**
- `query` (required): Search query
- `user_id` (required): User ID
- `limit` (optional): Number of results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "note_id": "uuid",
      "title": "string",
      "content": "string",
      "score": 0.95
    }
  ]
}
```

#### **PATCH /notes/:id**
Update existing note.

**Request:**
```json
{
  "title": "string",
  "content": "string"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "updated_at": "timestamp"
}
```

#### **DELETE /notes/:id**
Delete note (moves to trash).

**Response:**
```json
{
  "message": "Note deleted successfully"
}
```

---

## Challenges & Solutions

### Challenge 1: Semantic Search Needed to Understand Meaning

**Problem:** Traditional keyword search failed when users couldn't remember exact wording.

**Solution:** Integrated OpenAI's `text-embedding-3-small` model to convert notes into vector embeddings representing semantic meaning. Stored embeddings in Pinecone vector database for fast similarity search.

**Result:** Users can now find notes by concept rather than keywords (e.g., searching "AI projects" finds notes about "neural networks" and "machine learning").

---

### Challenge 2: AI Responses Needed Context from Entire Knowledge Base

**Problem:** GPT-4 alone couldn't access user's personal notes to provide relevant answers.

**Solution:** Built a Retrieval-Augmented Generation (RAG) pipeline:
1. Query Pinecone for semantically similar notes
2. Retrieve full note content from Supabase
3. Pass retrieved notes as context to GPT-4o-mini
4. Synthesize personalized answer based on user's knowledge base

**Result:** AI can answer questions like "What did I learn about React hooks?" using only information from the user's notes.

---

### Challenge 3: Managing Authentication Across Multiple Providers

**Problem:** Implementing secure authentication for email/password, Google OAuth, and GitHub OAuth from scratch would be complex and time-consuming.

**Solution:** Leveraged Supabase Auth for unified authentication handling. Supabase provides:
- Built-in email/password authentication
- OAuth integration with Google and GitHub
- Automatic JWT token management
- Row-level security (RLS) policies

**Result:** Secure, production-ready authentication with minimal code.

---

### Challenge 4: Auto-Indexing Notes Without Slowing Down Saves

**Problem:** Generating embeddings and updating Pinecone on every note save could slow down the user experience.

**Solution:** Implemented asynchronous indexing:
1. Note saved to Supabase immediately (fast response to user)
2. Embedding generation and Pinecone update happen asynchronously in the background
3. Frontend shows note as "saved" while indexing completes

**Result:** Responsive UI with seamless auto-indexing for search.

---

## Future Enhancements

Planned improvements for NeuralOS:

- [ ] **Note Sharing** - Share notes with other users via unique links
- [ ] **Collaborative Editing** - Real-time collaborative note editing
- [ ] **Mobile App** - React Native mobile application
- [ ] **Voice Input** - Record voice notes with speech-to-text
- [ ] **Advanced Markdown** - Support for code blocks, tables, LaTeX math
- [ ] **Export Options** - Export notes to PDF, Markdown, or plain text
- [ ] **Version History** - Track changes and restore previous versions
- [ ] **Tags & Categories** - Manual organization alongside semantic search
- [ ] **Offline Mode** - PWA with offline support and sync
- [ ] **Browser Extension** - Quick capture from any webpage
- [ ] **Analytics Dashboard** - Insights into note-taking patterns
- [ ] **Custom Embeddings** - Fine-tuned embeddings for domain-specific notes

---

## Contributing

Contributions are welcome! This is a personal portfolio project, but I'm open to suggestions and improvements.

**To contribute:**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Please ensure:**
- Code follows existing style conventions
- All tests pass (if applicable)
- New features include documentation updates

---

## License

This project is available as a reference for portfolio purposes. While the code is open source for learning, please don't directly copy this project without significant modification. Build something that represents your unique skills and experience.

---

## Contact

**Nick Wyrwas**
Software Engineering Graduate | U.S. Marine Corps Veteran

- **Portfolio**: [nickwyrwas.com](https://nickwyrwas.com)
- **Email**: nick.wyrwas@outlook.com
- **GitHub**: [github.com/nwyrwas](https://github.com/nwyrwas)
- **LinkedIn**: [linkedin.com/in/nicholas-wyrwas](https://linkedin.com/in/nicholas-wyrwas)

---

## Acknowledgments

Built with:
- [React](https://react.dev/) - Frontend library
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [OpenAI](https://openai.com/) - AI and embeddings
- [Pinecone](https://www.pinecone.io/) - Vector database
- [Supabase](https://supabase.com/) - Backend-as-a-Service

---

**Built by Nick Wyrwas** | [View Case Study](https://nickwyrwas.com/projects/neural-os)

*NeuralOS demonstrates full-stack development, AI/ML integration, and modern authentication patterns in a production-ready application.*
# neural-os
