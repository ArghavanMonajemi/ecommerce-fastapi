import enum

class CartStatus(enum.Enum):
    OPEN = "open"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"