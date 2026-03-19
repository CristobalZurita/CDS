from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.quote import Quote
from app.services.quote_management import (
    add_quote_item_to_quote,
    add_quote_recipient_to_quote,
    apply_quote_search,
    build_quote_board_snapshot,
    build_quote_query,
    create_quote_from_payload,
    delete_quote_if_unlinked,
    delete_quote_item_from_quote,
    delete_quote_recipient_from_quote,
    get_quote_or_404,
    serialize_quotes_with_clients,
    serialize_quote_with_client,
    send_quote_to_recipients,
    update_quote_from_payload,
    update_quote_item_on_quote,
    update_quote_status_from_payload,
)

router = APIRouter(tags=["quotes"])


def require_quote_permission(action: str):
    """
    Compatibilidad no destructiva:
    permite permisos nuevos (`quotes:*`) y legacy (`diagnostics:*`).
    """

    async def checker(
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        from app.services.permission_service import PermissionService

        user_id = user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Usuario no identificado")
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="ID de usuario inválido")

        svc = PermissionService(db)
        if svc.has_permission(user_id, "quotes", action) or svc.has_permission(
            user_id, "diagnostics", action
        ):
            return user

        raise HTTPException(
            status_code=403,
            detail=f"No tiene permiso para {action} en quotes/diagnostics",
        )

    return checker


@router.get("")
async def list_quotes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    query = build_quote_query(db.query(Quote), status=status, client_id=client_id)
    quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
    return serialize_quotes_with_clients(db, quotes)


@router.get("/board")
async def quote_board(
    skip: int = 0,
    limit: int = 200,
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    query = build_quote_query(db.query(Quote), status=status, client_id=client_id)
    query = apply_quote_search(query, q)
    quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
    return build_quote_board_snapshot(db, quotes)


@router.post("")
async def create_quote(
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("create")),
):
    return create_quote_from_payload(db, quote_data, user)


@router.get("/{quote_id}")
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("read")),
):
    quote = get_quote_or_404(db, quote_id)
    return serialize_quote_with_client(db, quote)


@router.put("/{quote_id}")
async def update_quote(
    quote_id: int,
    quote_data: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return update_quote_from_payload(db, quote, quote_data, user)


@router.delete("/{quote_id}")
async def delete_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return delete_quote_if_unlinked(db, quote)


@router.post("/{quote_id}/status")
async def update_quote_status(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("approve")),
):
    quote = get_quote_or_404(db, quote_id)
    return update_quote_status_from_payload(db, quote, payload, user)


@router.post("/{quote_id}/send")
async def send_quote(
    quote_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return send_quote_to_recipients(
        db,
        quote,
        payload,
        background_tasks=background_tasks,
        user=user,
    )


@router.post("/{quote_id}/items")
async def add_quote_item(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return add_quote_item_to_quote(db, quote, payload)


@router.put("/{quote_id}/items/{item_id}")
async def update_quote_item(
    quote_id: int,
    item_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return update_quote_item_on_quote(db, quote, item_id, payload)


@router.delete("/{quote_id}/items/{item_id}")
async def delete_quote_item(
    quote_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return delete_quote_item_from_quote(db, quote, item_id)


@router.post("/{quote_id}/recipients")
async def add_quote_recipient(
    quote_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return add_quote_recipient_to_quote(db, quote, payload)


@router.delete("/{quote_id}/recipients/{recipient_id}")
async def delete_quote_recipient(
    quote_id: int,
    recipient_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_quote_permission("update")),
):
    quote = get_quote_or_404(db, quote_id)
    return delete_quote_recipient_from_quote(db, quote, recipient_id)


def build_router(*, deprecated: bool = False) -> APIRouter:
    fresh_router = APIRouter(tags=["quotes"])
    fresh_router.add_api_route("", list_quotes, methods=["GET"], deprecated=deprecated)
    fresh_router.add_api_route("/board", quote_board, methods=["GET"], deprecated=deprecated)
    fresh_router.add_api_route("", create_quote, methods=["POST"], deprecated=deprecated)
    fresh_router.add_api_route("/{quote_id}", get_quote, methods=["GET"], deprecated=deprecated)
    fresh_router.add_api_route("/{quote_id}", update_quote, methods=["PUT"], deprecated=deprecated)
    fresh_router.add_api_route("/{quote_id}", delete_quote, methods=["DELETE"], deprecated=deprecated)
    fresh_router.add_api_route(
        "/{quote_id}/status",
        update_quote_status,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/send",
        send_quote,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/items",
        add_quote_item,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/items/{item_id}",
        update_quote_item,
        methods=["PUT"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/items/{item_id}",
        delete_quote_item,
        methods=["DELETE"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/recipients",
        add_quote_recipient,
        methods=["POST"],
        deprecated=deprecated,
    )
    fresh_router.add_api_route(
        "/{quote_id}/recipients/{recipient_id}",
        delete_quote_recipient,
        methods=["DELETE"],
        deprecated=deprecated,
    )
    return fresh_router
