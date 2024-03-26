
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session


from utils.getUserByToken import get_current_user


from database import  get_db

from schemas.Response.Response import Response

from schemas.Request.DocsUpdate import DocsUpdate
from schemas.Request.DocsCreate import DocsCreate
from schemas.Response.Docs import Docs



from models.Doc import Doc

from models.SharedDoc import SharedDoc


router = APIRouter(prefix="/me/docs", tags=["Docs"])



@router.delete("/{doc_id}")
def deleteDocs(doc_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return {"message": "Unauthorized", "success": False}

    doc = db.query(Doc).filter(Doc.owner_id == user["id"], Doc.id == doc_id).first()
    if not doc:
        return {"message": "Doc not found", "success": False}

    db.delete(doc)
    db.commit()
    return {"message": "Doc deleted", "success": True}


@router.patch("/{doc_id}", response_model=Response)
def updateDocs(doc_id: int, new_doc: DocsUpdate, db: Session = Depends(get_db),
               user=Depends(get_current_user)):
    if not user:
        return {"message": "Unauthorized", "success": False}

    # check if user is the owner of the document
    doc = db.query(Doc).filter(Doc.owner_id == user["id"], Doc.id == doc_id).first()
    if not doc:
        # check if the document is shared with the user
        shared_doc = db.query(Doc).join(SharedDoc).filter(SharedDoc.user_id == user["id"],
                                                                        SharedDoc.doc_id == doc_id,
                                                                        SharedDoc.edit_access == True).first()

        if not shared_doc:
            return {"message": "Doc does not exist or User don't have access", "success": False}

        doc = shared_doc

    if (new_doc.title):
        doc.title = new_doc.title
    if (new_doc.description):
        doc.description = new_doc.description

    db.commit()
    db.refresh(doc)
    return {"message": "Doc updated successfully", "success": True}


@router.get("/")
def getDocs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return {"message": "Unauthorized", "success": False}

    docs = db.query(Doc).filter(Doc.owner_id == user["id"]).all()
    return docs


@router.get("/shared_with_me/")
def getSharedDocs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return {"message": "Unauthorized", "success": False}

    shared_docs = db.query(Doc).join(SharedDoc).filter(SharedDoc.user_id == user["id"]).all()
    return shared_docs


@router.post("/", response_model=Docs)
def create_doc(doc: DocsCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return {"message": "Unauthorized", "success": False}

    db_doc = Doc(title=doc.title, description=doc.description, owner_id=user["id"])
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    print(db_doc)
    return db_doc
