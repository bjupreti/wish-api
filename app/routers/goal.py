from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..oauth2 import get_current_user
from ..models.goal import Goal as GoalModel
from ..schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from ..database import get_db

router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=GoalResponse)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_goal = GoalModel(**goal.dict(), user_id=current_user.id)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal

@router.get("/", response_model=list[GoalResponse])
def get_goals(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user), limit: int = 10, page: int = 1):
    offset = (page - 1) * limit
    goals = db.query(GoalModel).filter(GoalModel.user_id == current_user.id).order_by(GoalModel.created_at.desc()).limit(limit).offset(offset).all()
    return goals

@router.get("/{id}", response_model=GoalResponse)
def get_goal(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    goal = db.query(GoalModel).filter_by(id=str(id)).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"goal with id: {id} doesn't exist.")

    if goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized to perform requested action")

    return goal

@router.delete("/{id}")
def delete_goal(id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    goal_query = db.query(GoalModel).filter_by(id=str(id))
    goal = goal_query.first()

    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"goal with id: {id} doesn't exist.")

    if goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Not Authorized to perform requested action")

    goal_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=GoalResponse)
def update_goal(id: int, updated_goal: GoalUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    goal_query = db.query(GoalModel).filter_by(id=str(id))
    goal = goal_query.first()

    if goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"goal with id: {id} doesn't exist.")

    if goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Not Authorized to perform requested action")

    goal_query.update(updated_goal.dict(), synchronize_session=False)
    db.commit()
    return goal_query.first()

