from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from core.schema import NewUserResponseModel, UserModel
from core.outline import OutlineBackend

TOKEN = "d59cf216daaf407d81ddda6a98fc0e77"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(req: Request):
    token = req.headers["x-api-key"]
    if token != TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return True


@app.post("/api/v1/createOutlineUser/", status_code=201, response_model=NewUserResponseModel)
async def create_new_user(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        outline = OutlineBackend()
        _username = request.headers.get('name')
        _limit = request.headers.get('limit')
        user_data = outline.create_new_key(_username, _limit)

        _response = {
            "status": "success",
            "data": user_data,
        }

        return JSONResponse(content=_response)


@app.post("/api/v1/disableOutlineUser/", status_code=201, response_model=UserModel)
async def disable_user(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        outline = OutlineBackend()
        _username = request.headers.get('name')

        user_data = outline.disable_user(_username)
        _response = {
            "status": "success",
            "data": user_data,
        }
        return JSONResponse(content=_response)


@app.post("/api/v1/deleteOutlineUser/", status_code=201, response_model=UserModel)
async def delete_user(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        outline = OutlineBackend()
        _username = request.headers.get('name')

        user_data = outline.delete_key(_username)
        _response = {
            "status": "success",
            "data": user_data,
        }
        return JSONResponse(content=_response)


@app.post("/api/v1/setLimitOutlineUser/", status_code=201, response_model=NewUserResponseModel)
async def set_user_limit(request: Request, authorized: bool = Depends(verify_token)):
    if authorized:
        outline = OutlineBackend()
        _username = request.headers.get('name')
        _limit = request.headers.get('limit')

        user_data = outline.set_data_limit(_username, _limit)

        _response = {
            "status": "success",
            "data": user_data,
        }

        return JSONResponse(content=_response)


@app.get("/api/v1/getOutlineUser/", status_code=200, response_model=UserModel)
async def get_user(name: str, authorized: bool = Depends(verify_token)):
    if authorized:
        outline = OutlineBackend()
        user_data = outline.get_user(name)
        _response = {
            "access_url": user_data["access_url"],
            "key_id": user_data["key_id"],
            "name": user_data["name"],
            "status": "success",
        }
        return JSONResponse(content=_response)
