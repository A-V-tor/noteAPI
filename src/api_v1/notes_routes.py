from fastapi import APIRouter, HTTPException, status, Depends, Request, Header
from src.api_v1.schemas import AllNotesSchema, NewNoteSchema, EditNoteBody
from src.database.models import User, Note, Tag
from src.auth import JWTBearer


router = APIRouter(prefix='/api/v1')


async def get_current_user_id(request: Request):
    user_id = request.state.payload['user_id']
    if user_id and isinstance(user_id, int):
        return user_id

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get('/notes', dependencies=[Depends(JWTBearer())], tags=["notes"], response_model=list[AllNotesSchema])
async def get_notes(user_id: int = Depends(get_current_user_id)):
    notes = await Note.get_all_notes(user_id)

    return [AllNotesSchema.model_validate(note) for note in notes]


@router.post('/note/create', dependencies=[Depends(JWTBearer())], tags=["notes"])
async def create_note(note: NewNoteSchema, user_id: int = Depends(get_current_user_id)):
    tags = await Tag.get_tags_by_title(note.tags)
    new_note = await Note.create_note(user_id, note.title, note.text, tags)

    return new_note


@router.delete('/note/delete/{note_id}', dependencies=[Depends(JWTBearer())], tags=["notes"])
async def delete_note(note_id: int, user_id: int = Depends(get_current_user_id)):
    await Note.delete_note(note_id)

    return {"status": True}


@router.put('/note/edit/{note_id}', dependencies=[Depends(JWTBearer())], tags=["notes"])
async def edit_note(note_id: int, note_body: EditNoteBody, user_id: int = Depends(get_current_user_id)):
    text = note_body.text

    user_notes = await Note.get_note(user_id)
    user_notes_ids = [note.id for note in user_notes] if user_notes else []

    if note_id not in user_notes_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to the note is forbidden")

    await Note.edit_note(note_id, text)

    return {"status": True}


@router.put('/note/edit-tags/{note_id}', dependencies=[Depends(JWTBearer())], tags=["notes"])
async def edit_tags_note(tags: list[str], note_id: int, user_id: int = Depends(get_current_user_id)):
    user_notes = await Note.get_note(user_id)
    user_notes_ids = [note.id for note in user_notes] if user_notes else []

    if note_id not in user_notes_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to the note is forbidden")

    await Note.edit_tags_note(note_id, tags)

    return {"status": True}
