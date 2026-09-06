import re


def generate_receipt_number() -> str:
    """Genera un numero de recibo unico: timestamp con microsegundos + aleatorio.

    Los microsegundos evitan colisiones entre pagos registrados en el mismo segundo.
    """
    from datetime import datetime
    import random
    now = datetime.now()
    rand = random.randint(100, 999)
    return now.strftime("R%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}" + str(rand)


def generate_product_code() -> str:
    """Genera código único con microsegundos + aleatorio para evitar colisión."""
    from datetime import datetime
    import random
    now = datetime.now()
    rand = random.randint(100, 999)
    return now.strftime("PRD%Y%m%d%H%M%S") + f"{now.microsecond // 1000:03d}" + str(rand)


def clean_dni(dni: str) -> str:
    return re.sub(r"\D", "", dni)


def clean_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone)


def format_money(amount: float) -> str:
    return f"S/{amount:.2f}"


def truncate_text(text: str, max_length: int = 50) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
