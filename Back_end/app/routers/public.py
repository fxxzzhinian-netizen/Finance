"""公开（不需要登录）的资产展示接口，供二维码扫码访问。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/api/public", tags=["公开访问 (二维码)"])


@router.get(
    "/assets/{token}",
    response_model=schemas.PublicAssetOut,
    summary="按 public_token 获取资产的公开字段（无需登录）",
)
def get_public_asset(token: str, db: Session = Depends(get_db)):
    asset = crud.get_asset_by_public_token(db, token)
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在或链接已失效")
    return asset


@router.get(
    "/supplies/{serial_number}",
    response_model=schemas.PublicSupplyOut,
    summary="按序列号获取物资记录公开字段（无需登录）",
)
def get_public_supply(serial_number: str, db: Session = Depends(get_db)):
    record = crud.get_supply_by_serial(db, serial_number)
    if not record:
        raise HTTPException(status_code=404, detail="物资记录不存在或链接已失效")
    return record
