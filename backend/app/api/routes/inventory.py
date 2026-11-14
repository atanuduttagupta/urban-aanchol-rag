from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.schemas.inventory import (
    InventoryResponse,
    ReservationCheckRequest,
    ReservationDecisionResponse,
)
from backend.app.database.connection import get_database_connection
from backend.app.inventory.inventory_repository import (
    PostgresInventoryRepository,
)
from backend.app.inventory.inventory_service import InventoryService

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
