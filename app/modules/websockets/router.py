from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.modules.auth.helpers.decode_access_token import decode_access_token

from .connection_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/notifications")
async def notifications(websocket: WebSocket):

    token = websocket.query_params.get("token")
    payload = decode_access_token(token)

    if payload is None:
        await websocket.close(code=1008)
        return None

    user_id = payload.get("sub")
    # TODO: Implement the below logic later to check for disabled users etc.
    # user = await db.get(User, UUID(user_id)) 
    if user_id is None:
      await websocket.close(code=1008)
      return

    await manager.connect(
        str(user_id),
        websocket,
    )

    try:
      while True:
          await websocket.receive_text()

    except WebSocketDisconnect:
      pass

    finally:
      manager.disconnect(str(user_id), websocket)