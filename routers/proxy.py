from fastapi import APIRouter, Path, Depends, Response 
from sqlmodel import Session
from typing import Optional
import httpx
print(__name__)
from dependencies import security 

#from main import get_session, Session  


router = APIRouter(
    prefix="/proxy"
    #tags=[],
    #dependencies=[],
    #responses
)



@router.get("/{path:path}/{suffix:str}", tags=["Proxy"])
async def get_proxy(
    *,
    path: str,
    suffix: Optional[str] = Path(
        title="The suffix of the domain (com, org, net, etc...)",
        default="com"
    ), 
    response: Response,
    session: Session = Depends(security.get_session)
):
    """
    Attempt to proxy webpage:

    - **domain**: Specify the domain to proxy to
    - **suffix**: Specify the domain suffix (com, org, net, etc...)
    """
    async with httpx.AsyncClient() as client:
        proxy = await client.get(f"https://{path}.{suffix}")
    response.body = proxy.content
    response.status_code = proxy.status_code
    return response
