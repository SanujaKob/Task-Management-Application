from datetime import date
from typing import Optional, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from task_manager_app.core.deps import get_db
from task_manager_app.models.task import Task, Priority, Status
from task_manager_app.models.user import User, Role
from task_manager_app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from task_manager_app.routers.users import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _apply_filters(stmt, *,
                   status_: Optional[str],
                   priority: Optional[str],
                   assignee_id: Optional[int],
                   due_before: Optional[date],
                   due_after: Optional[date],
                   q: Optional[str]):
    conditions = []
    if status_:
        try:
            conditions.append(Task.status == Status(status_))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    if priority:
        try:
            conditions.append(Task.priority == Priority(priority))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid priority")
    if assignee_id is not None:
        conditions.append(Task.assignee_id == assignee_id)
    if due_before:
        conditions.append(Task.due_date != None)  # noqa: E711
        conditions.append(Task.due_date <= due_before)
    if due_after:
        conditions.append(Task.due_date != None)  # noqa: E711
        conditions.append(Task.due_date >= due_after)
    if q:
        like = f"%{q}%"
        conditions.append(or_(Task.title.ilike(like),
                              Task.description.ilike(like)))
    if conditions:
        stmt = stmt.where(and_(*conditions))
    return stmt


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate,
                db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    # Non-admin/manager cannot assign tasks to others
    if payload.assignee_id and current.role not in (Role.admin, Role.manager):
        raise HTTPException(status_code=403, detail="Only managers/admins can assign tasks")

    task = Task(
        title=payload.title,
        description=payload.description,
        priority=Priority(payload.priority),
        status=Status(payload.status),
        progress=payload.progress,
        due_date=payload.due_date,
        assignee_id=payload.assignee_id or current.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    status_: Annotated[Optional[str], Query(alias="status")] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    due_before: Optional[date] = None,
    due_after: Optional[date] = None,
    q: Optional[str] = None,
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum number of tasks to return")] = 100,
    offset: Annotated[int, Query(ge=0, description="Number of tasks to skip")] = 0,
):
    stmt = select(Task)
    # Regular users only see their own tasks
    if current.role not in (Role.admin, Role.manager):
        stmt = stmt.where(Task.assignee_id == current.id)
    stmt = _apply_filters(stmt, status_=status_, priority=priority,
                          assignee_id=assignee_id, due_before=due_before,
                          due_after=due_after, q=q)
    stmt = stmt.limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int,
             db: Session = Depends(get_db),
             current: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    if current.role not in (Role.admin, Role.manager) and task.assignee_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate,
                db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    # Only admin/manager or the assignee can update
    if current.role not in (Role.admin, Role.manager) and task.assignee_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Only admin/manager can reassign
    if payload.assignee_id is not None and current.role not in (Role.admin, Role.manager):
        raise HTTPException(status_code=403, detail="Only managers/admins can reassign")

    data = payload.model_dump(exclude_unset=True)

    if "priority" in data:
        data["priority"] = Priority(data["priority"])
    if "status" in data:
        data["status"] = Status(data["status"])

    for k, v in data.items():
        setattr(task, k, v)

    # Sanity: auto progress adjust on status change
    if "status" in data:
        if task.status == Status.completed:
            task.progress = 100
        elif task.status == Status.not_started and ("progress" not in data):
            task.progress = 0

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int,
                db: Session = Depends(get_db),
                current: User = Depends(get_current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    if current.role not in (Role.admin, Role.manager) and task.assignee_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(task)
    db.commit()
    return None
