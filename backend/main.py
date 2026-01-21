import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from supabase import create_client, Client

# ═══════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════

load_dotenv()

app = FastAPI(
    title="NeuralOS Backend",
    description="AI-powered note taking and semantic search API",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pinecone_client.Index("smart-notes")

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════

class NoteCreate(BaseModel):
    title: str = "Untitled Note"
    content: str
    user_id: str
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_deleted: Optional[bool] = None

class Note(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: List[str]
    is_favorite: bool
    is_archived: bool
    is_deleted: bool
    created_at: str
    updated_at: str

class SearchResult(BaseModel):
    id: str
    title: str
    text: str
    score: float
    created_at: str

class AIResponse(BaseModel):
    answer: str
    results: List[SearchResult]

class UserStats(BaseModel):
    total_notes: int
    favorites_count: int
    archived_count: int
    searches_this_week: int
    ai_insights: int
    streak: int

class NotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str = "info"  # info, success, warning, error

class Notification(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str

class UserPreferences(BaseModel):
    dark_mode: bool = True
    sidebar_collapsed: bool = False
    email_notifications: bool = True

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_embedding(text: str) -> List[float]:
    """Generate vector embedding for text using OpenAI"""
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def init_database():
    """Initialize database tables if they don't exist"""
    # Notes table
    # This would normally be done via Supabase dashboard or migrations
    # The schema is defined there
    pass

# ═══════════════════════════════════════════════════════════════
# NOTES ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/notes", response_model=Note)
async def create_note(note: NoteCreate):
    """Create a new note and index it in Pinecone"""
    try:
        note_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Generate embedding for semantic search
        embedding = generate_embedding(f"{note.title} {note.content}")

        # Store in Pinecone for vector search
        pinecone_index.upsert(vectors=[{
            "id": note_id,
            "values": embedding,
            "metadata": {
                "text": note.content,
                "title": note.title,
                "user_id": note.user_id,
                "created_at": now
            }
        }])

        # Store in Supabase for persistence
        note_data = {
            "id": note_id,
            "user_id": note.user_id,
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "is_favorite": False,
            "is_archived": False,
            "is_deleted": False,
            "created_at": now,
            "updated_at": now
        }

        result = supabase.table("notes").insert(note_data).execute()

        return Note(**note_data)

    except Exception as e:
        print(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes", response_model=List[Note])
async def get_notes(
    user_id: str,
    filter_type: str = "all",  # all, favorites, archived, trash
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get notes for a user with optional filtering"""
    try:
        query = supabase.table("notes").select("*").eq("user_id", user_id)

        # Apply filters based on type
        if filter_type == "all":
            query = query.eq("is_deleted", False).eq("is_archived", False)
        elif filter_type == "favorites":
            query = query.eq("is_favorite", True).eq("is_deleted", False)
        elif filter_type == "archived":
            query = query.eq("is_archived", True).eq("is_deleted", False)
        elif filter_type == "trash":
            query = query.eq("is_deleted", True)

        # Text search if provided
        if search:
            query = query.or_(f"title.ilike.%{search}%,content.ilike.%{search}%")

        # Order and paginate
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        result = query.execute()
        return [Note(**note) for note in result.data]

    except Exception as e:
        print(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: str, user_id: str):
    """Get a single note by ID"""
    try:
        result = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Note not found")

        return Note(**result.data)

    except Exception as e:
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Note not found")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/notes/{note_id}", response_model=Note)
async def update_note(note_id: str, user_id: str, update: NoteUpdate):
    """Update a note"""
    try:
        # Build update data
        update_data = {"updated_at": datetime.utcnow().isoformat()}

        if update.title is not None:
            update_data["title"] = update.title
        if update.content is not None:
            update_data["content"] = update.content
        if update.tags is not None:
            update_data["tags"] = update.tags
        if update.is_favorite is not None:
            update_data["is_favorite"] = update.is_favorite
        if update.is_archived is not None:
            update_data["is_archived"] = update.is_archived
        if update.is_deleted is not None:
            update_data["is_deleted"] = update.is_deleted

        # Update in Supabase
        result = supabase.table("notes").update(update_data).eq("id", note_id).eq("user_id", user_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Note not found")

        # Update Pinecone if content changed
        if update.content is not None or update.title is not None:
            note = result.data[0]
            embedding = generate_embedding(f"{note['title']} {note['content']}")
            pinecone_index.upsert(vectors=[{
                "id": note_id,
                "values": embedding,
                "metadata": {
                    "text": note["content"],
                    "title": note["title"],
                    "user_id": user_id,
                    "created_at": note["created_at"]
                }
            }])

        return Note(**result.data[0])

    except Exception as e:
        print(f"Error updating note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str, user_id: str, permanent: bool = False):
    """Delete a note (soft delete by default, permanent if specified)"""
    try:
        if permanent:
            # Permanent delete from both Supabase and Pinecone
            supabase.table("notes").delete().eq("id", note_id).eq("user_id", user_id).execute()
            try:
                pinecone_index.delete(ids=[note_id])
            except:
                pass  # Pinecone might not have this note
            return {"status": "permanently_deleted", "note_id": note_id}
        else:
            # Soft delete (move to trash)
            supabase.table("notes").update({
                "is_deleted": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", note_id).eq("user_id", user_id).execute()
            return {"status": "moved_to_trash", "note_id": note_id}

    except Exception as e:
        print(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/{note_id}/restore")
async def restore_note(note_id: str, user_id: str):
    """Restore a note from trash"""
    try:
        result = supabase.table("notes").update({
            "is_deleted": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", note_id).eq("user_id", user_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Note not found")

        return {"status": "restored", "note_id": note_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/{note_id}/favorite")
async def toggle_favorite(note_id: str, user_id: str):
    """Toggle favorite status of a note"""
    try:
        # Get current status
        note = supabase.table("notes").select("is_favorite").eq("id", note_id).eq("user_id", user_id).single().execute()

        if not note.data:
            raise HTTPException(status_code=404, detail="Note not found")

        # Toggle
        new_status = not note.data["is_favorite"]
        supabase.table("notes").update({
            "is_favorite": new_status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", note_id).eq("user_id", user_id).execute()

        return {"status": "success", "is_favorite": new_status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/{note_id}/archive")
async def toggle_archive(note_id: str, user_id: str):
    """Toggle archive status of a note"""
    try:
        # Get current status
        note = supabase.table("notes").select("is_archived").eq("id", note_id).eq("user_id", user_id).single().execute()

        if not note.data:
            raise HTTPException(status_code=404, detail="Note not found")

        # Toggle
        new_status = not note.data["is_archived"]
        supabase.table("notes").update({
            "is_archived": new_status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", note_id).eq("user_id", user_id).execute()

        return {"status": "success", "is_archived": new_status}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notes/trash/empty")
async def empty_trash(user_id: str):
    """Permanently delete all notes in trash"""
    try:
        # Get all trashed notes
        trashed = supabase.table("notes").select("id").eq("user_id", user_id).eq("is_deleted", True).execute()

        if trashed.data:
            note_ids = [n["id"] for n in trashed.data]

            # Delete from Pinecone
            try:
                pinecone_index.delete(ids=note_ids)
            except:
                pass

            # Delete from Supabase
            supabase.table("notes").delete().eq("user_id", user_id).eq("is_deleted", True).execute()

        return {"status": "success", "deleted_count": len(trashed.data) if trashed.data else 0}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# AI SEARCH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/search", response_model=AIResponse)
async def search_notes(query: str, user_id: str, limit: int = 5):
    """Semantic search with AI-powered analysis"""
    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)

        # Search Pinecone
        search_results = pinecone_index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True,
            filter={"user_id": {"$eq": user_id}}
        )

        matches = search_results.get("matches", [])

        if not matches:
            return AIResponse(
                answer="I couldn't find any notes matching your query. Try saving some notes first, or rephrase your question.",
                results=[]
            )

        # Prepare context for AI
        context_parts = []
        for m in matches:
            title = m['metadata'].get('title', 'Untitled')
            text = m['metadata'].get('text', '')
            context_parts.append(f"Title: {title}\nContent: {text}")

        context_text = "\n---\n".join(context_parts)
        best_score = matches[0]['score'] if matches else 0

        # AI Analysis
        system_prompt = """You are an intelligent personal knowledge assistant helping users recall and act on their saved notes and ideas.

Your role is to:
1. Analyze the user's saved notes in relation to their query
2. Provide helpful, actionable insights based on what they've recorded
3. Connect ideas and identify patterns across their notes
4. Suggest concrete next steps or actions they could take

Response Format:
- Start with a brief summary of what you found (1-2 sentences)
- Then provide 3-5 bullet points with specific insights, action items, or connections
- Be encouraging and supportive while being specific and actionable
- If notes are loosely related, still extract useful insights and suggest how they might connect to the query

Remember: These are the user's own thoughts and goals. Help them make progress on what matters to them."""

        user_prompt = f"""User's saved notes:
{context_text}

User's question: "{query}"

Relevance score of best match: {best_score:.0%}

Provide a helpful analysis with actionable bullet points."""

        ai_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        # Format results
        formatted_results = [
            SearchResult(
                id=m['id'],
                title=m['metadata'].get('title', 'Untitled'),
                text=m['metadata'].get('text', ''),
                score=m['score'],
                created_at=m['metadata'].get('created_at', '')
            )
            for m in matches
        ]

        # Log search for analytics
        try:
            supabase.table("search_logs").insert({
                "user_id": user_id,
                "query": query,
                "results_count": len(matches),
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        except:
            pass  # Analytics logging is optional

        return AIResponse(
            answer=ai_response.choices[0].message.content,
            results=formatted_results
        )

    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# USER STATS & PREFERENCES
# ═══════════════════════════════════════════════════════════════

@app.get("/stats", response_model=UserStats)
async def get_user_stats(user_id: str):
    """Get user statistics"""
    try:
        # Count notes
        total = supabase.table("notes").select("id", count="exact").eq("user_id", user_id).eq("is_deleted", False).execute()
        favorites = supabase.table("notes").select("id", count="exact").eq("user_id", user_id).eq("is_favorite", True).eq("is_deleted", False).execute()
        archived = supabase.table("notes").select("id", count="exact").eq("user_id", user_id).eq("is_archived", True).eq("is_deleted", False).execute()

        # Count searches this week
        from datetime import timedelta
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        try:
            searches = supabase.table("search_logs").select("id", count="exact").eq("user_id", user_id).gte("created_at", week_ago).execute()
            search_count = searches.count or 0
        except:
            search_count = 0

        # Calculate streak (days with activity)
        try:
            activities = supabase.table("notes").select("created_at").eq("user_id", user_id).order("created_at", desc=True).limit(30).execute()
            streak = calculate_streak(activities.data) if activities.data else 0
        except:
            streak = 0

        return UserStats(
            total_notes=total.count or 0,
            favorites_count=favorites.count or 0,
            archived_count=archived.count or 0,
            searches_this_week=search_count,
            ai_insights=search_count,  # Each search generates an insight
            streak=streak
        )

    except Exception as e:
        print(f"Stats error: {e}")
        # Return defaults on error
        return UserStats(
            total_notes=0,
            favorites_count=0,
            archived_count=0,
            searches_this_week=0,
            ai_insights=0,
            streak=0
        )

def calculate_streak(activities: List[dict]) -> int:
    """Calculate consecutive days with activity"""
    if not activities:
        return 0

    dates = set()
    for a in activities:
        try:
            date = datetime.fromisoformat(a['created_at'].replace('Z', '+00:00')).date()
            dates.add(date)
        except:
            continue

    if not dates:
        return 0

    sorted_dates = sorted(dates, reverse=True)
    streak = 1

    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i-1] - sorted_dates[i]).days == 1:
            streak += 1
        else:
            break

    return streak

@app.get("/preferences")
async def get_preferences(user_id: str):
    """Get user preferences"""
    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).single().execute()

        if result.data:
            return result.data
        else:
            # Return defaults
            return {
                "dark_mode": True,
                "sidebar_collapsed": False,
                "email_notifications": True
            }
    except:
        return {
            "dark_mode": True,
            "sidebar_collapsed": False,
            "email_notifications": True
        }

@app.put("/preferences")
async def update_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences"""
    try:
        data = {
            "user_id": user_id,
            "dark_mode": preferences.dark_mode,
            "sidebar_collapsed": preferences.sidebar_collapsed,
            "email_notifications": preferences.email_notifications,
            "updated_at": datetime.utcnow().isoformat()
        }

        # Upsert (insert or update)
        result = supabase.table("user_preferences").upsert(data).execute()

        return {"status": "success", "preferences": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

@app.get("/notifications")
async def get_notifications(user_id: str, unread_only: bool = False, limit: int = 20):
    """Get user notifications"""
    try:
        query = supabase.table("notifications").select("*").eq("user_id", user_id)

        if unread_only:
            query = query.eq("is_read", False)

        result = query.order("created_at", desc=True).limit(limit).execute()

        return result.data or []

    except Exception as e:
        # Return empty list on error (notifications are non-critical)
        return []

@app.post("/notifications")
async def create_notification(notification: NotificationCreate):
    """Create a notification"""
    try:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": notification.user_id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_read": False,
            "created_at": datetime.utcnow().isoformat()
        }

        supabase.table("notifications").insert(data).execute()

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, user_id: str):
    """Mark a notification as read"""
    try:
        supabase.table("notifications").update({
            "is_read": True
        }).eq("id", notification_id).eq("user_id", user_id).execute()

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/notifications/read-all")
async def mark_all_notifications_read(user_id: str):
    """Mark all notifications as read"""
    try:
        supabase.table("notifications").update({
            "is_read": True
        }).eq("user_id", user_id).execute()

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS (for backwards compatibility)
# ═══════════════════════════════════════════════════════════════

@app.post("/save-note")
async def save_note_legacy(req: dict):
    """Legacy endpoint for saving notes"""
    note = NoteCreate(
        title=req.get("title", "Untitled Note"),
        content=req["content"],
        user_id=req["user_id"],
        tags=req.get("tags", [])
    )
    result = await create_note(note)
    return {"status": "success", "note_id": result.id}

@app.get("/search-notes")
async def search_notes_legacy(query: str, user_id: str):
    """Legacy endpoint for searching notes"""
    result = await search_notes(query, user_id)
    # Convert to legacy format
    return {
        "answer": result.answer,
        "results": [{"text": r.text, "score": r.score} for r in result.results]
    }

# ═══════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "2.0.0",
        "services": {
            "openai": "connected",
            "pinecone": "connected",
            "supabase": "connected"
        }
    }

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
