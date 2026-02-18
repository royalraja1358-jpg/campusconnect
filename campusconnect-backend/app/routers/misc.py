from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random, string
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import (
    User, Announcement, Reminder, HostelComplaint, LostFound,
    FeeDetail, CanteenShop, MenuItem, CanteenOrder, CartItem,
    BusRoute, LibraryBook, LibraryBorrow, Staff
)
from app.schemas.schemas import (
    AnnouncementOut, ReminderCreate, ReminderOut,
    ComplaintCreate, ComplaintOut, LostFoundCreate, LostFoundOut,
    FeeOut, ShopOut, MenuItemOut, OrderCreate, OrderOut,
    CartAddRequest, BusRouteOut, BookOut, BorrowOut
)

router = APIRouter(tags=["Misc"])


# ─── Announcements ──────────────────────────────────────────

@router.get("/api/announcements", response_model=List[AnnouncementOut])
def get_announcements(db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return db.query(Announcement).order_by(Announcement.created_at.desc()).limit(20).all()


# ─── Reminders ──────────────────────────────────────────────

@router.get("/api/reminders", response_model=List[ReminderOut])
def get_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_done == False
    ).order_by(Reminder.remind_at).all()


@router.post("/api/reminders", response_model=ReminderOut)
def add_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    r = Reminder(user_id=current_user.id, **data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/api/reminders/{rid}")
def delete_reminder(
    rid: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    r = db.query(Reminder).filter(Reminder.id == rid, Reminder.user_id == current_user.id).first()
    if not r:
        raise HTTPException(404, "Reminder not found")
    db.delete(r)
    db.commit()
    return {"message": "Deleted"}


# ─── Hostel Complaints ──────────────────────────────────────

@router.get("/api/hostel/complaints", response_model=List[ComplaintOut])
def get_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(HostelComplaint).filter(
        HostelComplaint.student_id == current_user.id
    ).order_by(HostelComplaint.created_at.desc()).all()


@router.post("/api/hostel/complaints", response_model=ComplaintOut)
def raise_complaint(
    data: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    ticket = "HC" + datetime.now().strftime("%Y") + "-" + \
             ''.join(random.choices(string.digits, k=4))
    c = HostelComplaint(student_id=current_user.id, ticket_no=ticket, **data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ─── Lost & Found ───────────────────────────────────────────

@router.get("/api/lost-found", response_model=List[LostFoundOut])
def get_lost_found(db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    items = db.query(LostFound).order_by(LostFound.created_at.desc()).limit(30).all()
    return [LostFoundOut(
        id=i.id, item_name=i.item_name, description=i.description,
        status=i.status, location=i.location, contact=i.contact,
        posted_by=i.posted_by_user.name if i.posted_by_user else "Anonymous",
        is_resolved=i.is_resolved, created_at=i.created_at
    ) for i in items]


@router.post("/api/lost-found", response_model=LostFoundOut)
def post_lost_found(
    data: LostFoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = LostFound(posted_by=current_user.id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return LostFoundOut(
        id=item.id, item_name=item.item_name, description=item.description,
        status=item.status, location=item.location, contact=item.contact,
        posted_by=current_user.name, is_resolved=item.is_resolved,
        created_at=item.created_at
    )


# ─── Fee Details ────────────────────────────────────────────

@router.get("/api/fees", response_model=List[FeeOut])
def get_fees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    profile = current_user.profile
    semester = profile.semester if profile else 6
    fees = db.query(FeeDetail).filter(
        FeeDetail.student_id == current_user.id,
        FeeDetail.semester == semester
    ).all()
    return [FeeOut(
        fee_type=f.fee_type, amount=f.amount, is_paid=f.is_paid,
        paid_at=f.paid_at, receipt_no=f.receipt_no, due_date=f.due_date
    ) for f in fees]


# ─── Canteen ────────────────────────────────────────────────

@router.get("/api/canteen/shops", response_model=List[ShopOut])
def get_shops(db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    shops = db.query(CanteenShop).all()
    return [ShopOut(
        id=s.id, name=s.name, block=s.block, emoji=s.emoji, is_open=s.is_open,
        menu_items=[MenuItemOut(
            id=m.id, name=m.name, price=m.price,
            is_available=m.is_available, category=m.category
        ) for m in s.menu_items if m.is_available]
    ) for s in shops]


@router.get("/api/canteen/shops/{shop_id}", response_model=ShopOut)
def get_shop(shop_id: int, db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    s = db.query(CanteenShop).filter(CanteenShop.id == shop_id).first()
    if not s:
        raise HTTPException(404, "Shop not found")
    return ShopOut(
        id=s.id, name=s.name, block=s.block, emoji=s.emoji, is_open=s.is_open,
        menu_items=[MenuItemOut(
            id=m.id, name=m.name, price=m.price,
            is_available=m.is_available, category=m.category
        ) for m in s.menu_items]
    )


@router.post("/api/canteen/cart/add")
def add_to_cart(
    data: CartAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    item = db.query(MenuItem).filter(MenuItem.id == data.menu_item_id).first()
    if not item:
        raise HTTPException(404, "Menu item not found")
    existing = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.menu_item_id == data.menu_item_id
    ).first()
    if existing:
        existing.quantity += data.quantity
    else:
        db.add(CartItem(user_id=current_user.id,
                        menu_item_id=data.menu_item_id, quantity=data.quantity))
    db.commit()
    return {"message": f"{item.name} added to cart"}


@router.get("/api/canteen/cart")
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    result = []
    total = 0.0
    for ci in items:
        mi = db.query(MenuItem).filter(MenuItem.id == ci.menu_item_id).first()
        if mi:
            subtotal = mi.price * ci.quantity
            total += subtotal
            result.append({
                "cart_item_id": ci.id,
                "menu_item_id": mi.id,
                "name": mi.name,
                "price": mi.price,
                "quantity": ci.quantity,
                "subtotal": subtotal,
                "shop_id": mi.shop_id,
            })
    return {"items": result, "total": total}


@router.post("/api/canteen/order", response_model=OrderOut)
def place_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    shop = db.query(CanteenShop).filter(CanteenShop.id == data.shop_id).first()
    if not shop or not shop.is_open:
        raise HTTPException(400, "Shop closed or not found")

    total = 0.0
    items_snapshot = []
    for it in data.items:
        mi = db.query(MenuItem).filter(MenuItem.id == it["menu_item_id"]).first()
        if not mi:
            raise HTTPException(404, f"Menu item {it['menu_item_id']} not found")
        qty = it.get("quantity", 1)
        sub = mi.price * qty
        total += sub
        items_snapshot.append({"name": mi.name, "qty": qty, "price": mi.price, "subtotal": sub})

    order = CanteenOrder(
        student_id=current_user.id,
        shop_id=data.shop_id,
        items=items_snapshot,
        total=total,
        status="pending",
    )
    db.add(order)
    # Clear cart for this shop
    cart_ids = [it["menu_item_id"] for it in data.items]
    db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.menu_item_id.in_(cart_ids)
    ).delete(synchronize_session=False)
    db.commit()
    db.refresh(order)
    return OrderOut(
        id=order.id, shop_id=order.shop_id, items=order.items,
        total=order.total, status=order.status, ordered_at=order.ordered_at
    )


# ─── Teacher on Leave ───────────────────────────────────────

@router.get("/api/teacher-leave")
def get_teachers_on_leave(db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    staff_on_leave = db.query(Staff).filter(Staff.is_on_leave == True).all()
    return [{
        "id": s.id,
        "staff_no": s.staff_no,
        "name": s.name,
        "designation": s.designation,
        "leave_date": s.leave_date.isoformat() if s.leave_date else None,
        "subjects": [sub.code + " " + sub.name for sub in s.subjects],
    } for s in staff_on_leave]


# ─── Bus Tracking ───────────────────────────────────────────

@router.get("/api/bus", response_model=List[BusRouteOut])
def get_bus_routes(db: Session = Depends(get_db), _=Depends(get_current_active_user)):
    return db.query(BusRoute).all()


# ─── Library ────────────────────────────────────────────────

@router.get("/api/library/borrowed", response_model=List[BorrowOut])
def get_borrowed_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    borrows = db.query(LibraryBorrow).filter(
        LibraryBorrow.student_id == current_user.id,
        LibraryBorrow.returned_at == None
    ).all()
    result = []
    for b in borrows:
        book = db.query(LibraryBook).filter(LibraryBook.id == b.book_id).first()
        if book:
            result.append(BorrowOut(
                id=b.id, title=book.title, author=book.author,
                accession_no=book.accession_no, borrowed_at=b.borrowed_at,
                due_date=b.due_date, returned_at=b.returned_at, fine=b.fine
            ))
    return result


@router.get("/api/library/search", response_model=List[BookOut])
def search_books(
    q: str = "",
    db: Session = Depends(get_db),
    _=Depends(get_current_active_user)
):
    books = db.query(LibraryBook).filter(
        LibraryBook.title.ilike(f"%{q}%") | LibraryBook.author.ilike(f"%{q}%")
    ).limit(20).all()
    return [BookOut(
        id=b.id, title=b.title, author=b.author,
        accession_no=b.accession_no, available=b.available
    ) for b in books]
