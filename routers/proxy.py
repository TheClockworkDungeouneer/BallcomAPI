from fastapi import APIRouter, Path, Depends, Response, Request
from sqlmodel import Session
from typing import Optional
import httpx
from httpx import AsyncClient
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from dependencies import security 

#from main import get_session, Session  


router = APIRouter(
    prefix="/proxy"
    #tags=[],
    #dependencies=[],
    #responses
)
HTTP_SERVER = AsyncClient(base_url="http://localhost:8000=")

async def _reverse_proxy(request: Request):
    path = (request.url.path).split("proxy/")[-1] 
    url = httpx.URL(path=path, query=request.url.query.encode("utf-8"))
    print("da path: ", path)
    rp_req = HTTP_SERVER.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    rp_resp = await HTTP_SERVER.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )

## statement below breaks whole router:

#router.add_route("/{path:path}", _reverse_proxy, ["GET", "POST"])




'''
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
'''
