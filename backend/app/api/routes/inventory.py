from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.app.api.schemas.inventory import (
    CreateHoldRequest,
    HoldCreationResponse,
    InventoryResponse,
    ReservationCheckRequest,
    ReservationDecisionResponse,
)
from backend.app.database.connection import get_database_connection
from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.inventory_service import InventoryService
from backend.app.inventory.models import ReservationReason

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


def get_inventory_service() -> Generator[InventoryService, None, None]:
    connection = get_database_connection()

    try:
        repository = PostgresInventoryRepository(connection)
        yield InventoryService(repository)
    finally:
        connection.close()


@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory(
    product_id: str,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> InventoryResponse:
    inventory = service.get_inventory(product_id)

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return InventoryResponse(
        product_id=inventory.product_id,
        stock_quantity=inventory.stock_quantity,
        reserved_quantity=inventory.reserved_quantity,
        available_quantity=inventory.available_quantity,
        admin_availability=inventory.admin_availability,
        customer_availability=inventory.customer_availability,
        can_reserve=inventory.can_reserve,
    )


@router.post(
    "/check-reservation",
    response_model=ReservationDecisionResponse,
)
def check_reservation(
    request: ReservationCheckRequest,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> ReservationDecisionResponse:
    decision = service.check_reservation(
        request.product_id,
        request.quantity,
    )

    return ReservationDecisionResponse(
        allowed=decision.allowed,
        product_id=decision.product_id,
        requested_quantity=decision.requested_quantity,
        available_quantity=decision.available_quantity,
        customer_availability=decision.customer_availability,
        reason=decision.reason,
    )


@router.post(
    "/create-hold",
    response_model=HoldCreationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hold(
    request: CreateHoldRequest,
    response: Response,
    service: Annotated[InventoryService, Depends(get_inventory_service)],
) -> HoldCreationResponse:
    result = service.create_hold(
        product_id=request.product_id,
        quantity=request.quantity,
        customer_reference=request.customer_reference,
        notes=request.notes,
    )

    if result.created:
        response.status_code = status.HTTP_201_CREATED
    elif result.reason == ReservationReason.PRODUCT_NOT_FOUND:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_409_CONFLICT

    return HoldCreationResponse(
        created=result.created,
        hold_id=result.hold_id,
        product_id=result.product_id,
        requested_quantity=result.requested_quantity,
        available_quantity=result.available_quantity,
        customer_availability=result.customer_availability,
        reason=result.reason,
    )
