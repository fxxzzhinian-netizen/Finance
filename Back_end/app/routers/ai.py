"""AI 辅助接口：自然语言搜索解析等。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .. import models
from ..llm_client import LLMUnavailable, is_configured, parse_search_query
from ..security import get_current_user

router = APIRouter(
    prefix="/api/ai",
    tags=["AI 辅助"],
    dependencies=[Depends(get_current_user)],
)


class ParseSearchIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="用户自然语言搜索文本")
    target: str = Field("assets", description="搜索目标：assets 或 logs")


class ParseSearchOut(BaseModel):
    params: dict = Field(default_factory=dict, description="解析出的结构化查询参数")


@router.post(
    "/parse-search",
    response_model=ParseSearchOut,
    summary="AI 搜索：将自然语言转为结构化查询参数",
)
def ai_parse_search(payload: ParseSearchIn):
    if not is_configured():
        raise HTTPException(
            status_code=400,
            detail="后端未配置百炼 API Key，无法使用 AI 搜索。",
        )
    if payload.target not in ("assets", "logs"):
        raise HTTPException(status_code=400, detail="target 只能是 assets 或 logs")
    try:
        params = parse_search_query(payload.text, target=payload.target)
    except LLMUnavailable as e:
        raise HTTPException(status_code=502, detail=f"AI 解析失败：{e}") from e
    return {"params": params}
