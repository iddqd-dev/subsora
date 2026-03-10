from pydantic import BaseModel, EmailStr, Field, model_validator


class BootstrapStatus(BaseModel):
    needs_bootstrap: bool


class BootstrapAdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_password_strength(self) -> "BootstrapAdminCreate":
        pwd = self.password
        has_alpha = any(ch.isalpha() for ch in pwd)
        has_digit = any(ch.isdigit() for ch in pwd)
        if not (has_alpha and has_digit):
            raise ValueError("Password must contain both letters and numbers")
        return self
