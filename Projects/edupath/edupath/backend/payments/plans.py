from dataclasses import dataclass
from typing import List

@dataclass
class TokenPackage:
    id: str
    name: str
    tokens: float
    price_paise: int
    price_display: str
    bonus_percentage: int = 0

    @property
    def actual_tokens(self) -> float:
        return self.tokens * (1 + self.bonus_percentage / 100)

class PricingPlans:
    TOKEN_PACKAGES = [
        TokenPackage("starter", "Starter Pack", 100, 49900, "₹499"),
        TokenPackage("power", "Power Pack", 500, 199900, "₹1,999", 10),
        TokenPackage("ultimate", "Ultimate Pack", 1000, 349900, "₹3,499", 20),
    ]

    @classmethod
    def get_package_by_id(cls, package_id: str):
        for pkg in cls.TOKEN_PACKAGES:
            if pkg.id == package_id:
                return pkg
        raise ValueError(f"Package not found: {package_id}")
