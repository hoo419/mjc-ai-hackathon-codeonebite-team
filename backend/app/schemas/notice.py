from pydantic import BaseModel


class Notice(BaseModel):
    """Mirrors API_CONTRACT.md section 9. `category` is left as a free
    string - the contract doesn't enumerate allowed values, so we don't
    invent an enum it never defined."""

    id: str
    title: str
    category: str
    publishedAt: str
    url: str


class NoticeListResponse(BaseModel):
    notices: list[Notice]
