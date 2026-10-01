from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StrictBool


class Source(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=300)
    url: HttpUrl
    text: str = Field(min_length=20, max_length=12000)
    published_at: date | None = None

class Finding(BaseModel):
    model_config = ConfigDict(extra='forbid')
    headline: str = Field(min_length=1, max_length=200)
    category: Literal['product', 'funding', 'partnership', 'other']
    source_id: str
    quote: str = Field(min_length=20, max_length=1500)
    implication: str = Field(min_length=1, max_length=1200)

class Findings(BaseModel):
    model_config = ConfigDict(extra='forbid')
    findings: list[Finding] = Field(min_length=1, max_length=20)

class Critique(BaseModel):
    model_config = ConfigDict(extra='forbid')
    concerns: list[str] = Field(max_length=20)

class Approval(BaseModel):
    model_config = ConfigDict(extra='forbid')
    approved: StrictBool
    reviewer: str = Field(min_length=2, max_length=100)
    note: str = Field(min_length=3, max_length=2000)
