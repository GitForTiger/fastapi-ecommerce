from pydantic import (
    BaseModel, 
    Field, 
    AnyUrl,
    field_validator,
    model_validator,
    computed_field,
    EmailStr
    )
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime, timezone


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

    @field_validator("email",mode = "after") # this "after" converts the input(string) to it's preferred datatype
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

    # field_validator works on only one field : SKU here.
    @field_validator("sku",mode = "after") # this "after" converts the input(string) to it's preferred datatype
    @classmethod
    def validate_sku_format(cls, value : str):
        if "-" not in value:
            raise ValueError("SKU must have '-'")
        last = value.split("-")[-1]
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit sequence like -234")
        return value
    
    # model_validator works on more than one field
    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.stock == 0 and self.is_active == True:
            raise ValueError("If stock is 0, is_active must be false")
        return self
        
    #Note: mode="after" validators should use self (instance method), not @classmethod. 
    #The @classmethod decorator is only correct for mode="before".
    @computed_field
    @property
    def final_price(self) ->float:
        return round(self.price * (1-self.discount_percent/100),2)
    
    @computed_field
    @property
    def volume_c3(self) ->float:
        d = self.dimensions_cm
        return round(d.length * d.width * d.height, 2)