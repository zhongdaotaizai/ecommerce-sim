from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.simulation_runner import _run_simulation_day, _initialize_system_data
from app.schemas.market import SimDayResult
import threading

router = APIRouter()
_sim_lock = threading.Lock()

@router.post("/day", response_model=SimDayResult)
def trigger_simulate_day(db: Session = Depends(get_db)):
    if not _sim_lock.acquire(blocking=False):
        raise HTTPException(400, "Simulation already running")
    try:
        result = _run_simulation_day(db)
        return SimDayResult(
            day=result.get("day", 0),
            orders_created=result.get("orders_created", 0),
            events_triggered=result.get("events_triggered", []),
            revenue_generated=result.get("revenue_generated", 0.0),
            message=result.get("message", "Completed"),
        )
    finally:
        _sim_lock.release()

@router.get("/status")
def get_simulation_status(db: Session = Depends(get_db)):
    from app.models.event import SimState
    state = db.query(SimState).first()
    if not state:
        return {"current_day": 0, "is_running": False, "total_orders": 0, "total_revenue": 0}
    running = bool(state.is_running) or _sim_lock.locked()
    return {"current_day": state.current_day, "is_running": running, "last_run_at": state.last_run_at, "total_orders": state.total_orders_placed, "total_revenue": state.total_revenue}

@router.post("/reset")
def reset_simulation(db: Session = Depends(get_db)):
    from app.models.event import SimState
    state = db.query(SimState).first()
    if state:
        state.current_day = 0
        state.is_running = 0
        state.total_orders_placed = 0
        state.total_revenue = 0.0
        state.last_run_at = None
        db.commit()
    return {"message": "Simulation reset"}

@router.post("/init")
def initialize_data(db: Session = Depends(get_db)):
    from app.core.database import create_tables
    create_tables()
    result = _initialize_system_data(db)
    return {"message": f"System initialization completed: {result.get('message', '')}"}
