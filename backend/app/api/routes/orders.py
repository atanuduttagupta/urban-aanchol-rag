
from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, status

from backend.app.api.schemas.orders import (
    OrderCreateRequest,
    OrderCreationResponse,
    OrderItemResponse,
    OrderResponse,
)
from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.database.connection import get_database_connection
from backend.app.orders.delivery_charge import DeliveryChargeConfigurationError
from backend.app.orders.exceptions import (
    CustomerNotFoundError,
    HoldConflictError,
    HoldNotFoundError,
    InsufficientInventoryError,
    ProductNotFoundError,
    ProductPriceNotConfiguredError,
    ProductUnavailableError,
)
from backend.app.orders.idempotency import IdempotencyConflictError
from backend.app.orders.models import (
    CreateOrderRequest,
    OrderItemRequest,
    OrderStatus,
)
from backend.app.orders.order_repository import PostgresOrderRepository
from backend.app.orders.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def get_order_service() -> Generator[OrderService, None, None]:
    connection = get_database_connection()

    try:
        order_repository = PostgresOrderRepository(connection)
        customer_repository = PostgresCustomerRepository(connection)

        yield OrderService(
            order_repository=order_repository,
            customer_repository=customer_repository,
        )
    finally:
        connection.close()


@router.post(
    "",
    response_model=OrderCreationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    request: OrderCreateRequest,
    service: Annotated[OrderService, Depends(get_order_service)],
    idempotency_key: Annotated[
        UUID,
        Header(alias="Idempotency-Key"),
    ],
) -> OrderCreationResponse:
    try:
        domain_request = CreateOrderRequest(
            customer_id=request.customer_id,
            items=tuple(
                OrderItemRequest(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    notes=item.notes,
                    hold_id=item.hold_id,
                )
                for item in request.items
            ),
            expected_delivery_date=request.expected_delivery_date,
            ship_to_contact_name=request.ship_to_contact_name,
            ship_to_phone=request.ship_to_phone,
            ship_to_address=request.ship_to_address,
            notes=request.notes,
        )

        result = service.create_order(
            request=domain_request,
            idempotency_key=idempotency_key,
        )

    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        ) from exc

    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more products were not found.",
        ) from exc

    except HoldNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more inventory holds were not found.",
        ) from exc

    except (
        HoldConflictError,
        ProductUnavailableError,
        InsufficientInventoryError,
        IdempotencyConflictError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except (
        ProductPriceNotConfiguredError,
        DeliveryChargeConfigurationError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Order placement is temporarily unavailable.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return OrderCreationResponse(
        order=OrderResponse.model_validate(result.order),
        items=[
            OrderItemResponse.model_validate(item)
            for item in result.items
        ],
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: Annotated[int, Path(gt=0)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> OrderResponse:
    order = service.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    return OrderResponse.model_validate(order)


@router.get(
    "/{order_id}/items",
    response_model=list[OrderItemResponse],
)
def get_order_items(
    order_id: Annotated[int, Path(gt=0)],
    service: Annotated[OrderService, Depends(get_order_service)],
) -> list[OrderItemResponse]:
    order = service.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    items = service.get_order_items(order_id)

    return [
        OrderItemResponse.model_validate(item)
        for item in items
    ]


@router.get(
    "",
    response_model=list[OrderResponse],
)
def list_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
    customer_id: int | None = None,
    order_status: OrderStatus | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[OrderResponse]:
    try:
        orders = service.list_orders(
            customer_id=customer_id,
            order_status=order_status,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return [
        OrderResponse.model_validate(order)
        for order in orders
    ]
