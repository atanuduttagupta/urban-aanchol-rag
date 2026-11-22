from uuid import UUID

from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.orders.delivery_charge import get_flat_delivery_charge
from backend.app.orders.models import (
    CreateOrderRequest,
    Order,
    OrderCreationResult,
    OrderItem,
    OrderStatus,
)
from backend.app.orders.order_repository import PostgresOrderRepository


class OrderService:
    """Application service for order management."""

    def __init__(
        self,
        order_repository: PostgresOrderRepository,
        customer_repository: PostgresCustomerRepository,
    ) -> None:
        if not isinstance(order_repository, PostgresOrderRepository):
            raise ValueError("Invalid order repository")

        if not isinstance(customer_repository, PostgresCustomerRepository):
            raise ValueError("Invalid customer repository")

        self.order_repository = order_repository
        self.customer_repository = customer_repository

    def create_order(
        self,
        request: CreateOrderRequest,
        idempotency_key: UUID,
    ) -> OrderCreationResult:
        if not isinstance(request, CreateOrderRequest):
            raise ValueError("request must be a CreateOrderRequest")

        if not isinstance(idempotency_key, UUID):
            raise ValueError("idempotency_key must be a UUID")

        if self.order_repository.connection is not self.customer_repository.connection:
            raise ValueError(
                "Order and customer repositories must share "
                "the same database connection"
            )

        delivery_charge = get_flat_delivery_charge()

        return self.order_repository.create_order(
            request=request,
            delivery_charge=delivery_charge,
            customer_repository=self.customer_repository,
            idempotency_key=idempotency_key,
        )

    @staticmethod
    def _validate_positive_id(
        field_name: str,
        value: int,
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer")

        if value <= 0:
            raise ValueError(f"{field_name} must be greater than zero")

    def get_order(self, order_id: int) -> Order | None:
        self._validate_positive_id("order_id", order_id)
        return self.order_repository.get_order(order_id)

    def get_order_items(
        self,
        order_id: int,
    ) -> list[OrderItem]:
        self._validate_positive_id("order_id", order_id)
        return self.order_repository.get_order_items(order_id)

    def list_orders(
        self,
        customer_id: int | None = None,
        order_status: OrderStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Order]:
        if customer_id is not None:
            self._validate_positive_id("customer_id", customer_id)

        if order_status is not None and not isinstance(
            order_status,
            OrderStatus,
        ):
            raise ValueError("Invalid order_status")

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit must be an integer")

        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")

        if isinstance(offset, bool) or not isinstance(offset, int):
            raise ValueError("offset must be an integer")

        if offset < 0:
            raise ValueError("offset cannot be negative")

        return self.order_repository.list_orders(
            customer_id=customer_id,
            order_status=order_status,
            limit=limit,
            offset=offset,
        )
