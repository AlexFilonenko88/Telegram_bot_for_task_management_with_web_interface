from datetime import datetime, timedelta
from typing import List, Optional
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models import Task, User, Team, Category, Tag
from app.schemas.task import TaskCreate, TaskUpdate, CategoryCreate, TagCreate
from app.schemas.user import UserCreate, TeamCreate


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user(db: Session, user_id: int) -> List[Task]:
    return db.query(Task).filter(Task.user_id == user_id).all()


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        priority=task.priority,
        deadline=task.deadline,
        category_id=task.category_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Add tags if provided
    if task.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(task.tag_ids)).all()
        db_task.tags = tags
        db.commit()
        db.refresh(db_task)

    return db_task


def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True, exclude={'tag_ids'})
    for field, value in update_data.items():
        setattr(db_task, field, value)

    # Handle completion timestamp
    if 'is_done' in update_data and update_data['is_done'] and not db_task.completed_at:
        db_task.completed_at = datetime.utcnow()

    # Update tags if provided
    if task_update.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(task_update.tag_ids)).all()
        db_task.tags = tags

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True


def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_or_create_user(db: Session, user: UserCreate) -> User:
    db_user = get_user_by_telegram_id(db, user.telegram_id)
    if db_user:
        return db_user
    return create_user(db, user)


def get_weekly_stats(db: Session, user_id: int) -> dict:
    """Get task completion statistics for the last 7 days."""
    tasks = get_tasks_by_user(db, user_id)
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    
    daily_stats = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        completed_on_day = sum(
            1 for task in tasks
            if task.is_done and day_start <= task.created_at <= day_end
        )
        
        daily_stats.append({
            "date": day.strftime("%Y-%m-%d"),
            "day_name": day.strftime("%A"),
            "completed": completed_on_day
        })
    
    total = len(tasks)
    done = len([t for t in tasks if t.is_done])
    active = total - done
    percentage = (done / total * 100) if total > 0 else 0
    
    return {
        "total": total,
        "done": done,
        "active": active,
        "percentage": round(percentage, 1),
        "daily_stats": daily_stats
    }


def get_team_by_name(db: Session, name: str) -> Optional[Team]:
    return db.query(Team).filter(Team.name == name).first()


def create_team(db: Session, team: TeamCreate) -> Team:
    db_team = Team(name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def add_user_to_team(db: Session, user_id: int, team_id: int) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    db_user.team_id = team_id
    db.commit()
    db.refresh(db_user)
    return db_user


def get_team_tasks(db: Session, team_id: int) -> List[Task]:
    return db.query(Task).join(User).filter(User.team_id == team_id).all()


def get_team_weekly_stats(db: Session, team_id: int) -> dict:
    """Get team task completion statistics for the last 7 days."""
    tasks = get_team_tasks(db, team_id)

    today = datetime.now().date()
    week_ago = today - timedelta(days=6)

    daily_stats = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        completed_on_day = sum(
            1 for task in tasks
            if task.is_done and day_start <= task.created_at <= day_end
        )

        daily_stats.append({
            "date": day.strftime("%Y-%m-%d"),
            "day_name": day.strftime("%A"),
            "completed": completed_on_day
        })

    total = len(tasks)
    done = len([t for t in tasks if t.is_done])
    active = total - done
    percentage = (done / total * 100) if total > 0 else 0

    return {
        "total": total,
        "done": done,
        "active": active,
        "percentage": round(percentage, 1),
        "daily_stats": daily_stats
    }


# Category CRUD
def get_categories_by_user(db: Session, user_id: int) -> List[Category]:
    return db.query(Category).filter(Category.user_id == user_id).all()


def get_category(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(
        name=category.name,
        user_id=category.user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if not db_category:
        return False

    db.delete(db_category)
    db.commit()
    return True


# Tag CRUD
def get_tags_by_user(db: Session, user_id: int) -> List[Tag]:
    return db.query(Tag).filter(Tag.user_id == user_id).all()


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id).first()


def create_tag(db: Session, tag: TagCreate) -> Tag:
    db_tag = Tag(
        name=tag.name,
        user_id=tag.user_id
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False

    db.delete(db_tag)
    db.commit()
    return True


# Task reminder functions
def get_tasks_with_upcoming_deadlines(db: Session, hours_ahead: int = 24) -> List[Task]:
    """Get tasks with deadlines within the next N hours that haven't been reminded."""
    now = datetime.utcnow()
    deadline_limit = now + timedelta(hours=hours_ahead)

    return db.query(Task).join(User).filter(
        Task.deadline.isnot(None),
        Task.deadline <= deadline_limit,
        Task.deadline > now,
        Task.reminder_sent == False,
        Task.is_done == False
    ).all()


def mark_reminder_sent(db: Session, task_id: int) -> bool:
    """Mark a task as having received a reminder."""
    db_task = get_task(db, task_id)
    if not db_task:
        return False

    db_task.reminder_sent = True
    db.commit()
    return True
