"""
FastAPI Backend for BizGenie AI
Endpoints for business plan generation and management
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from database import get_db, init_db, BusinessPlan as DBPlan
from models import (
    BusinessIdeaRequest,
    PlanResponse,
    GeneratePlanResponse,
)
from agents import run_agent_pipeline, AGENT_STEPS

# ─────────────────────────────────────────────
# App init
# ─────────────────────────────────────────────
app = FastAPI(
    title="BizGenie AI API",
    description="AI-powered business plan generator using Grok API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "BizGenie AI Backend is running 🚀", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
# Generate Plan (Streaming SSE)
# ─────────────────────────────────────────────
@app.post("/api/generate-plan")
def generate_plan_stream(request: BusinessIdeaRequest, db: Session = Depends(get_db)):
    """
    Stream business plan generation as Server-Sent Events.
    Each event carries the current step status and partial results.
    """
    # Create DB record
    db_plan = DBPlan(
        title=f"Plan {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        idea=request.idea,
        status="generating",
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    plan_id = db_plan.id

    def event_stream():
        collected_plan = {}

        def progress_cb(step_name: str, status: str, data=None):
            payload = json.dumps({
                "type": "progress",
                "step": step_name,
                "status": status,
                "data": data,
            })
            yield f"data: {payload}\n\n"

        # We need a generator-friendly approach
        # Collect yields from callback via a queue pattern
        import queue
        import threading

        q: queue.Queue = queue.Queue()

        def cb(step_name, status, data=None):
            q.put({"type": "progress", "step": step_name, "status": status, "data": data})

        error_container = [None]

        def run_pipeline():
            try:
                result = run_agent_pipeline(request.idea, progress_callback=cb)
                collected_plan.update(result)
                q.put({"type": "complete", "plan": result, "plan_id": plan_id})
            except Exception as e:
                q.put({"type": "error", "message": str(e)})
            finally:
                q.put(None)  # sentinel

        thread = threading.Thread(target=run_pipeline, daemon=True)
        thread.start()

        while True:
            item = q.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

        # Save to DB
        try:
            db_obj = db.query(DBPlan).filter(DBPlan.id == plan_id).first()
            if db_obj:
                db_obj.plan_data = collected_plan
                db_obj.status = "completed"
                db_obj.updated_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─────────────────────────────────────────────
# Generate Plan (Non-Streaming, full response)
# ─────────────────────────────────────────────
@app.post("/api/generate-plan-sync", response_model=dict)
def generate_plan_sync(request: BusinessIdeaRequest, db: Session = Depends(get_db)):
    """Generate full business plan synchronously (for Streamlit polling)."""
    # Create DB record
    db_plan = DBPlan(
        title=f"Plan - {request.idea[:40]}...",
        idea=request.idea,
        status="generating",
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    plan_id = db_plan.id

    steps_done = []

    def progress_cb(step_name: str, status: str, data=None):
        steps_done.append({"step": step_name, "status": status})

    try:
        result = run_agent_pipeline(request.idea, progress_callback=progress_cb)

        # Update DB
        db_plan.plan_data = result
        db_plan.status = "completed"
        db_plan.title = result.get("executive_summary", {}).get("company_name", db_plan.title)
        db_plan.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "plan_id": plan_id,
            "plan": result,
            "steps": steps_done,
        }
    except Exception as e:
        db_plan.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# Plans CRUD
# ─────────────────────────────────────────────
@app.get("/api/plans")
def list_plans(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    plans = (
        db.query(DBPlan)
        .order_by(DBPlan.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": p.id,
            "title": p.title,
            "idea": p.idea[:100] + "..." if len(p.idea) > 100 else p.idea,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in plans
    ]


@app.get("/api/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(DBPlan).filter(DBPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {
        "id": plan.id,
        "title": plan.title,
        "idea": plan.idea,
        "plan_data": plan.plan_data,
        "status": plan.status,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
    }


@app.delete("/api/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(DBPlan).filter(DBPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": f"Plan {plan_id} deleted successfully"}
