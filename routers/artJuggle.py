from fastapi import FastAPI, Depends


from dependancies import security
from dependancies.database import *


router = APIRouter(
    prefix="/artjuggle"
        ) 


@router.get("/")
def get_artjuggle(session: Session = Depends(security.get_session)):
    responeJSON = session
    
    return []

@router.post("/"):
def post_artjuggle(session: Session = Depends(security.get_session)):
    return session.select(ArtPost)



