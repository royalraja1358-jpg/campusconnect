from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import datetime

from app.core.database import get_db, SessionLocal
from app.core.security import get_current_active_user, decode_token
from app.models.user import User, Message, Notification
from app.schemas.schemas import MessageCreate, MessageOut
from app.utils.websocket_manager import manager

router = APIRouter(prefix="/api/messages", tags=["Messages"])


@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of all conversations (DMs + groups) with latest message."""
    # Direct messages
    sent = db.query(Message).filter(
        Message.sender_id == current_user.id,
        Message.receiver_id != None
    ).all()
    received = db.query(Message).filter(
        Message.receiver_id == current_user.id
    ).all()

    dm_partners = set()
    for m in sent:
        dm_partners.add(m.receiver_id)
    for m in received:
        dm_partners.add(m.sender_id)

    convs = []
    for uid in dm_partners:
        partner = db.query(User).filter(User.id == uid).first()
        if not partner:
            continue
        last = db.query(Message).filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == uid)) |
            ((Message.sender_id == uid) & (Message.receiver_id == current_user.id))
        ).order_by(Message.sent_at.desc()).first()
        unread = db.query(Message).filter(
            Message.sender_id == uid,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).count()
        convs.append({
            "type": "dm",
            "partner_id": uid,
            "partner_name": partner.name,
            "partner_reg": partner.reg_no,
            "last_message": last.content if last else "",
            "last_time": last.sent_at.isoformat() if last else "",
            "unread": unread,
        })

    # Groups
    group_messages = db.query(Message).filter(
        Message.group_name != None
    ).distinct(Message.group_name).all()
    seen_groups = set()
    for gm in group_messages:
        gn = gm.group_name
        if gn in seen_groups:
            continue
        seen_groups.add(gn)
        last = db.query(Message).filter(
            Message.group_name == gn
        ).order_by(Message.sent_at.desc()).first()
        convs.append({
            "type": "group",
            "group_name": gn,
            "last_message": last.content if last else "",
            "last_time": last.sent_at.isoformat() if last else "",
            "unread": 0,
        })

    convs.sort(key=lambda x: x["last_time"], reverse=True)
    return convs


@router.get("/dm/{partner_id}")
def get_dm_history(
    partner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    messages = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == partner_id)) |
        ((Message.sender_id == partner_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.sent_at).all()

    # Mark as read
    db.query(Message).filter(
        Message.sender_id == partner_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()

    return [_msg_out(m, db) for m in messages]


@router.get("/group/{group_name}")
def get_group_history(
    group_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    messages = db.query(Message).filter(
        Message.group_name == group_name
    ).order_by(Message.sent_at).all()
    return [_msg_out(m, db) for m in messages]


@router.post("/send")
async def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    msg = Message(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        group_name=data.group_name,
        content=data.content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    payload = {
        "type": "new_message",
        "id": msg.id,
        "sender_id": current_user.id,
        "sender_name": current_user.name,
        "content": data.content,
        "sent_at": msg.sent_at.isoformat(),
        "group_name": data.group_name,
        "receiver_id": data.receiver_id,
    }

    if data.receiver_id:
        await manager.send_to_user(data.receiver_id, payload)
    if data.group_name:
        await manager.broadcast_to_group(data.group_name, payload)

    return payload


def _msg_out(m: Message, db: Session) -> dict:
    sender = db.query(User).filter(User.id == m.sender_id).first()
    return {
        "id": m.id,
        "sender_id": m.sender_id,
        "sender_name": sender.name if sender else "Unknown",
        "content": m.content,
        "is_read": m.is_read,
        "sent_at": m.sent_at.isoformat(),
        "group_name": m.group_name,
        "receiver_id": m.receiver_id,
    }


# ─── WebSocket ──────────────────────────────────────────────

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Connect:  ws://localhost:8000/api/messages/ws/<JWT_TOKEN>
    After connecting, send JSON:
      {"action": "join_group", "group": "ChE-6A"}
      {"action": "send_dm",    "to": 5, "content": "hello"}
      {"action": "send_group", "group": "ChE-6A", "content": "hi all"}
    """
    try:
        payload = decode_token(token)
        reg_no = payload.get("sub")
    except Exception:
        await websocket.close(code=4001)
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.reg_no == reg_no).first()
        if not user:
            await websocket.close(code=4001)
            return

        await manager.connect_user(websocket, user.id)

        try:
            while True:
                raw = await websocket.receive_text()
                data = json.loads(raw)
                action = data.get("action")

                if action == "join_group":
                    group = data.get("group")
                    if group:
                        await manager.join_group(websocket, group)
                        await websocket.send_text(json.dumps({
                            "type": "system",
                            "message": f"Joined {group}"
                        }))

                elif action == "leave_group":
                    group = data.get("group")
                    if group:
                        manager.leave_group(websocket, group)

                elif action == "send_dm":
                    to_id = data.get("to")
                    content = data.get("content", "").strip()
                    if to_id and content:
                        msg = Message(sender_id=user.id, receiver_id=to_id, content=content)
                        db.add(msg)
                        db.commit()
                        db.refresh(msg)
                        out = {
                            "type": "new_message",
                            "id": msg.id,
                            "sender_id": user.id,
                            "sender_name": user.name,
                            "content": content,
                            "sent_at": msg.sent_at.isoformat(),
                            "receiver_id": to_id,
                        }
                        await manager.send_to_user(to_id, out)
                        await websocket.send_text(json.dumps({**out, "echo": True}))

                elif action == "send_group":
                    group = data.get("group")
                    content = data.get("content", "").strip()
                    if group and content:
                        msg = Message(sender_id=user.id, group_name=group, content=content)
                        db.add(msg)
                        db.commit()
                        db.refresh(msg)
                        out = {
                            "type": "new_message",
                            "id": msg.id,
                            "sender_id": user.id,
                            "sender_name": user.name,
                            "content": content,
                            "sent_at": msg.sent_at.isoformat(),
                            "group_name": group,
                        }
                        await manager.broadcast_to_group(group, out, exclude=websocket)
                        await websocket.send_text(json.dumps({**out, "echo": True}))

                elif action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

        except WebSocketDisconnect:
            manager.disconnect_user(websocket, user.id)
    finally:
        db.close()
