from dataclasses import dataclass

@dataclass
class GoogleRegisterDTO:
    credential: str
    password: str
    confirm_password: str
    rut: str | None = None