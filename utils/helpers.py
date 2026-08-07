import re


def generate_receipt_number() -> str:
    from datetime import datetime
    import random
    now = datetime.now()
    rand = random.randint(10, 99)
    return now.strftime("R%Y%m%d%H%M%S") + str(rand)


def generate_product_code() -> str:
    from datetime import datetime
    now = datetime.now()
    return now.strftime("PRD%Y%m%d%H%M%S")


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
