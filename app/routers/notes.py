from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.models import Note
from app.schemas.note import NoteCreate, NoteOut, NoteUpdate
from app.core.security.user import get_current_active_user
from app.schemas.user import UserOut

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)


@router.post("/", response_model=NoteOut)
async def create_note(
        note: NoteCreate,
        current_user: UserOut = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=current_user.id
    )
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.get("/", response_model=list[NoteOut])
async def get_notes(
        current_user: UserOut = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    statement = select(Note).where(Note.user_id == current_user.id)
    results = session.exec(statement).all()
    return results


@router.put("/{note_id}", response_model=NoteOut)
async def update_note(
        note_id: int,
        note_data: NoteUpdate,
        current_user: UserOut = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    statement = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    db_note = session.exec(statement).one_or_none()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    for key, value in note_data.dict(exclude_unset=True).items():
        setattr(db_note, key, value)

    db_note.updated_at = datetime.now(timezone.utc)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


@router.delete("/{note_id}")
async def delete_note(
        note_id: int,
        current_user: UserOut = Depends(get_current_active_user),
        session: Session = Depends(get_session),
):
    statement = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    db_note = session.exec(statement).one_or_none()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(db_note)
    session.commit()
    return {"detail": "Note deleted successfully"}
