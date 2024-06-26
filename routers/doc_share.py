import bcrypt
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from utils.getUserByToken import get_current_user

from database import get_db

from schemas.Response.Response import Response
from schemas.common.SharedDocBase import SharedDocBase

from models.Doc import Doc
from models.User import User
from models.SharedDoc import SharedDoc

router = APIRouter(prefix="/me/share", tags=["Docs Share"])


@router.post("/", response_model=Response)
def shareDocs(docShareDTO: SharedDocBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # check if user is the owner of the document
    doc = db.query(Doc).filter(Doc.owner_id == user["id"], Doc.id == docShareDTO.doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doc not found")

    # check if user mail exists
    target_user = db.query(User).filter(User.email == docShareDTO.user_mail).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    # check if user is trying to share the document with himself
    if doc.owner_id == target_user.id:
        raise HTTPException(status_code=400, detail="You can't share the document with yourself")

    # check if the document is already shared with the target_user

    shared_doc = db.query(SharedDoc).filter(SharedDoc.doc_id == docShareDTO.doc_id,
                                            SharedDoc.user_id == target_user.id).first()

    if shared_doc:
        raise HTTPException(status_code=400, detail="Doc already shared with the target user")

    # share the document
    doc_share = SharedDoc(doc_id=docShareDTO.doc_id, user_id=target_user.id, edit_access=docShareDTO.edit_access)
    db.add(doc_share)
    db.commit()
    db.refresh(doc_share)

    return {"message": "Doc shared", "success": True}


@router.patch("/", response_model=Response)
def updateShareAccess(docShareDTO: SharedDocBase, db: Session = Depends(get_db),
                      user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # check if user is the owner of the document
    doc = db.query(Doc).filter(Doc.owner_id == user["id"], Doc.id == docShareDTO.doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doc not found")

    # check if user mail exists
    target_user = db.query(User).filter(User.email == docShareDTO.user_mail).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    # check if user is trying to share the document with himself
    if doc.owner_id == target_user.id:
        raise HTTPException(status_code=400, detail="You can't share the document with yourself")

    # check if the document is already shared with the target_user

    shared_doc = db.query(SharedDoc).filter(SharedDoc.doc_id == docShareDTO.doc_id,
                                            SharedDoc.user_id == target_user.id).first()

    if not shared_doc:
        raise HTTPException(status_code=404, detail="Doc not shared with the target user")

    shared_doc.edit_access = docShareDTO.edit_access
    db.commit()
    db.refresh(shared_doc)

    return {"message": "Doc shared access updated", "success": True}


@router.delete("/", response_model=Response)
def deleteShare(docShareDTO: SharedDocBase, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # check if user is the owner of the document
    doc = db.query(Doc).filter(Doc.owner_id == user["id"], Doc.id == docShareDTO.doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doc not found")

    # check if user mail exists
    target_user = db.query(User).filter(User.email == docShareDTO.user_mail).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    # check if user is trying to share the document with himself
    if doc.owner_id == target_user.id:
        raise HTTPException(status_code=400, detail="You can't share the document with yourself")

    # check if the document is already shared with the target_user

    shared_doc = db.query(SharedDoc).filter(SharedDoc.doc_id == docShareDTO.doc_id,
                                            SharedDoc.user_id == target_user.id).first()

    if not shared_doc:
        raise HTTPException(status_code=404, detail="Doc not shared with the target user")

    db.delete(shared_doc)
    db.commit()

    return {"message": "Doc shared access deleted", "success": True}
