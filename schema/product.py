from pydantic import (
    BaseModel, 
    Field, 
    AnyUrl,
    field_validator,
    model_validator,
    computed_field,
    EmailStr,
    ConfigDict
    )
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime, timezone


# CREATE PYDANTIC


class DimensionsCM(BaseModel):
    length : Annotated[
        float, Field(
            gt=0,
            description="Length in cm"
        )
    ]
    width : Annotated[
        float, Field(
            gt=0,
            description="Width in cm"
        )
    ]
    height : Annotated[
        float, Field(
            gt=0,
            description="Height in cm"
        )
    ]


class Seller(BaseModel):
    seller_id: UUID
    
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=60,
            title="Seller Name",
            description="Name of the seller (2-60 chars)",
            examples=["ABC Store","XYZ Store"]
        )
    ]

    email : EmailStr

    website : AnyUrl

    @field_validator("email",mode = "after")
    @classmethod
    def validate_seller_email_domain(cls, value : str):
        allowed_domains = {
            "mistore.in",
            "realmeofficial.in",
            "samsungindia.in",
            "lenovostore.in",
            "hpworld.in",
            "applestoreindia.in",
            "dellexclusive.in",
            "sonycenter.in",
            "oneplusstore.in",
            "asusexclusive.in",
        }

        domain=value.split("@")[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed : {domain}")
        return value

class Products(BaseModel):
    product_id : UUID
    sku: Annotated[
        str,
        Field(
            description="The unique SKU of the product",
            examples=["WER-EDC-UHK-234"]
        )
    ]
    name: Annotated[
        str,
        Field(
            min_length=5,
            max_length=100,
            description="Name of the product",
            examples=["Organic Energy Bars"]
        )
    ]

    description: Annotated[
        str,
        Field(
            min_length=20,
            max_length=500,
            description="Detailed description of the product",
            examples=[
                "High-protein energy bars made with organic oats, honey, and dark chocolate."
            ]
        )
    ]

    price: Annotated[
        float,
        Field(
            gt=0,
            description="Product price. Must be greater than zero.",
            examples=[499.00]
        )
    ]

    discount_percent: Annotated[
        int,
        Field(
            gt=0,
            description="Percentage discount on the product"
        )
    ]
    currency: Literal["INR"] = "INR"

    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            description="Product category",
            examples=["Health & Nutrition"]
        )
    ]

    stock: Annotated[
        int,
        Field(
            ge=0,
            description="Available quantity of the product in stock",
            examples=[200]
        )
    ]

    is_active: Annotated[
        bool,
        Field(
            description="true if stock>0 otherwise false"
        )
    ]

    rating: Annotated[
        float,
        Field(
            ge=0,
            le=5,
            description="Average product rating between 0 and 5",
            examples=[4.5]
        )
    ]

    reviews_count: Annotated[
        int,
        Field(
            ge=0,
            description="Total number of customer reviews",
            examples=[312]
        )
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(
            default=None,
            max_length=10,
            description="Tags relating to the product"
        )
    ]

    image_urls: Annotated[
        List[AnyUrl],
        Field(
            min_length=1,
            description="Image URL(s)"
        )
    ]

    dimensions_cm : DimensionsCM
    seller : Seller

    created_at : datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the product was created"
    )

    @field_validator("sku",mode = "after")
    @classmethod
    def validate_sku_format(cls, value : str):
        if "-" not in value:
            raise ValueError("SKU must have '-'")
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit sequence like -234")
        return value
    
    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.stock == 0 and self.is_active == True:
            raise ValueError("If stock is 0, is_active must be false")
        return self
        
    @computed_field
    @property
    def final_price(self) ->float:
        return round(self.price * (1-self.discount_percent/100),2)
    
    @computed_field
    @property
    def volume_c3(self) ->float:
        d = self.dimensions_cm
        return round(d.length * d.width * d.height, 2)
    

# UPDATE PYDANTIC


class DimensionsCMUpdate(BaseModel):
    length : Optional[float] = Field(default=None, gt = 0)
    width : Optional[float] = Field(default=None, gt = 0)
    height : Optional[float] = Field(default=None, gt = 0)


class SellerUpdate(BaseModel):
    name : Optional[str] = Field(default=None, min_length = 2, max_length = 60)
    email : Optional[EmailStr] = None
    website : Optional[AnyUrl] = None

    @field_validator("email", mode="after")
    @classmethod
    def validate_seller_email_domain(cls, value : str):
        if value is None:
            return value
        allowed_domains = {
            "mistore.in",
            "realmeofficial.in",
            "samsungindia.in",
            "lenovostore.in",
            "hpworld.in",
            "applestoreindia.in",
            "dellexclusive.in",
            "sonycenter.in",
            "oneplusstore.in",
            "asusexclusive.in",
        }
        domain = value.split("@")[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed : {domain}")
        return value


class ProductUpdate(BaseModel):

    model_config = ConfigDict(extra="ignore")
    # This line ensures that the Pydantic ignores all those fields whose value the user does not specify at the time of update

    name : Optional[str] = Field(default=None, min_length = 3, max_length = 80)
    description : Optional[str] = Field(default=None, max_length = 200)
    category : Optional[str] = None
    brand : Optional[str] = None

    price : Optional[float] = Field(default=None, gt = 0)
    currency : Optional[Literal["INR"]] = None

    discount_percent: Optional[int] = Field(default=None, ge=0, le=90)
    stock: Optional[int] = Field(default=None, ge=0)

    is_active: Optional[bool] = None

    rating: Optional[float] = Field(default=None, ge=0, le=5)

    tags: Optional[List[str]] = Field(default=None, max_length=10)
    image_urls: Optional[List[AnyUrl]] = None

    dimensions_cm: Optional[DimensionsCMUpdate] = None
    seller: Optional[SellerUpdate] = None
    
    @model_validator(mode="after")
    def validate_business_rules(self):
        # Only validate if BOTH fields are present in this update payload
        if self.stock is not None and self.is_active is not None:
            if self.stock == 0 and self.is_active == True:
                raise ValueError("If stock is 0, is_active must be false")
        return self
        
    @computed_field
    @property
    def final_price(self) -> Optional[float]:
        if self.price is None or self.discount_percent is None:
            return None
        return round(self.price * (1 - self.discount_percent / 100), 2)
    
    @computed_field
    @property
    def volume_c3(self) -> Optional[float]:
        d = self.dimensions_cm
        if d is None or d.length is None or d.width is None or d.height is None:
            return None
        return round(d.length * d.width * d.height, 2)