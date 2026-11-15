from collections.abc import Generator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.api.schemas.customers import (
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
)
from backend.app.customers.customer_repository import (
    PostgresCustomerRepository,
)
from backend.app.customers.customer_service import CustomerService
from backend.app.database.connection import get_database_connection

router = APIRouter(prefix="/api/customers", tags=["Customers"])


def get_customer_service() -> Generator[CustomerService, None, None]:
    connection = get_database_connection()

    try:
        repository = PostgresCustomerRepository(connection)
        yield CustomerService(repository)
    finally:
        connection.close()


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    request: CustomerCreateRequest,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerResponse:
    try:
        customer = service.create_customer(request.model_dump())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return CustomerResponse.model_validate(customer)


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[CustomerResponse]:
    try:
        customers = service.list_customers(
            search=search,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return [
        CustomerResponse.model_validate(customer)
        for customer in customers
    ]


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerResponse:
    try:
        customer = service.get_customer(customer_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return CustomerResponse.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    request: CustomerUpdateRequest,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerResponse:
    updates = request.model_dump(exclude_unset=True)

    try:
        customer = service.update_customer(customer_id, updates)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return CustomerResponse.model_validate(customer)
