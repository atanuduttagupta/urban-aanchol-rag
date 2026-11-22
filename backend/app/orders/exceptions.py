"""Domain exceptions for order management."""


class OrderBusinessError(ValueError):
    """Base exception for expected order business failures."""


class CustomerNotFoundError(OrderBusinessError):
    """The requested customer does not exist."""


class ProductNotFoundError(OrderBusinessError):
    """One or more requested products do not exist."""


class HoldNotFoundError(OrderBusinessError):
    """One or more requested inventory holds do not exist."""


class HoldConflictError(OrderBusinessError):
    """An inventory hold cannot be converted into an order."""


class ProductUnavailableError(OrderBusinessError):
    """A product is not available for ordering."""


class ProductPriceNotConfiguredError(OrderBusinessError):
    """A product does not have a configured selling price."""


class InsufficientInventoryError(OrderBusinessError):
    """Insufficient available inventory for the requested quantity."""
