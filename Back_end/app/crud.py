"""资产 CRUD 操作。"""
import re
import secrets
from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from . import asset_code as code_util
from . import models, schemas
from .config import get_settings


_SUPPLY_SERIAL_RE = re.compile(r"^WZ-(\d{4})-(\d{6})$")


def _new_public_token() -> str:
    return secrets.token_urlsafe(16)


def next_supply_serial(db: Session) -> str:
    year = datetime.now().year
    prefix = f"WZ-{year}-"
    rows = db.execute(
        select(models.SupplyRecord.serial_number).where(
            models.SupplyRecord.serial_number.like(f"{prefix}%")
        )
    ).scalars()

    max_seq = 0
    for value in rows:
        match = _SUPPLY_SERIAL_RE.match(value or "")
        if not match:
            continue
        code_year = int(match.group(1))
        if code_year != year:
            continue
        max_seq = max(max_seq, int(match.group(2)))
    return f"{prefix}{max_seq + 1:06d}"


def list_assets(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    asset_class: Optional[str] = None,
    location: Optional[str] = None,
    owner: Optional[str] = None,
    department: Optional[str] = None,
    supplier: Optional[str] = None,
    brand: Optional[str] = None,
) -> Tuple[int, list[models.Asset]]:
    stmt = select(models.Asset)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                models.Asset.asset_code.like(like),
                models.Asset.brand.like(like),
                models.Asset.model.like(like),
                models.Asset.serial_number.like(like),
                models.Asset.owner.like(like),
            )
        )
    if status:
        stmt = stmt.where(models.Asset.status == status)
    if category:
        stmt = stmt.where(models.Asset.category == category)
    if asset_class:
        stmt = stmt.where(models.Asset.asset_class == asset_class.upper())
    if location:
        stmt = stmt.where(models.Asset.location.like(f"%{location}%"))
    if owner:
        stmt = stmt.where(models.Asset.owner.like(f"%{owner}%"))
    if department:
        stmt = stmt.where(models.Asset.department.like(f"%{department}%"))
    if supplier:
        stmt = stmt.where(models.Asset.supplier.like(f"%{supplier}%"))
    if brand:
        stmt = stmt.where(models.Asset.brand.like(f"%{brand}%"))

    total = len(db.execute(stmt).scalars().all())
    stmt = (
        stmt.order_by(models.Asset.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(stmt).scalars().all()
    return total, list(items)


def get_asset(db: Session, asset_id: int) -> Optional[models.Asset]:
    return db.get(models.Asset, asset_id)


def get_asset_by_code(db: Session, asset_code: str) -> Optional[models.Asset]:
    return db.execute(
        select(models.Asset).where(models.Asset.asset_code == asset_code)
    ).scalar_one_or_none()


def get_asset_by_public_token(
    db: Session, token: str
) -> Optional[models.Asset]:
    if not token:
        return None
    return db.execute(
        select(models.Asset).where(models.Asset.public_token == token)
    ).scalar_one_or_none()


def ensure_public_token(db: Session, asset: models.Asset) -> models.Asset:
    """如果资产没有 public_token 就生成一个并保存。"""
    if asset.public_token:
        return asset
    asset.public_token = _new_public_token()
    db.commit()
    db.refresh(asset)
    return asset


def regenerate_public_token(db: Session, asset: models.Asset) -> models.Asset:
    """强制刷新 public_token，使旧二维码失效。"""
    asset.public_token = _new_public_token()
    db.commit()
    db.refresh(asset)
    return asset


def create_asset(db: Session, payload: schemas.AssetCreate) -> models.Asset:
    settings = get_settings()
    data = payload.model_dump()

    asset_class = (data.get("asset_class") or "").upper().strip()
    if not asset_class:
        raise HTTPException(status_code=400, detail="资产大类不能为空")
    data["asset_class"] = asset_class

    code = (data.get("asset_code") or "").strip().upper()
    if not code:
        year = (
            data["purchase_date"].year
            if data.get("purchase_date")
            else datetime.now().year
        )
        code = code_util.generate_next_code(
            db, settings.org_code, asset_class, year
        )
    else:
        if not code_util.is_valid_code(code):
            raise HTTPException(
                status_code=400,
                detail="资产编号格式或校验位不正确，请使用「自动生成」或参照规则填写",
            )
        parsed = code_util.parse_code(code)
        if parsed and parsed["asset_class"] != asset_class:
            raise HTTPException(
                status_code=400,
                detail=f"资产编号中的大类({parsed['asset_class']})与所选大类({asset_class})不一致",
            )
    data["asset_code"] = code
    data["public_token"] = _new_public_token()

    asset = models.Asset(**data)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def update_asset(
    db: Session, asset: models.Asset, payload: schemas.AssetUpdate
) -> models.Asset:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(asset, key, value)
    db.commit()
    db.refresh(asset)
    return asset


def delete_asset(db: Session, asset: models.Asset) -> None:
    db.delete(asset)
    db.commit()


def list_asset_files(db: Session, asset_id: int) -> list[models.AssetFile]:
    stmt = (
        select(models.AssetFile)
        .where(models.AssetFile.asset_id == asset_id)
        .order_by(models.AssetFile.id.desc())
    )
    return list(db.execute(stmt).scalars().all())


def get_asset_file(db: Session, file_id: int) -> Optional[models.AssetFile]:
    return db.get(models.AssetFile, file_id)


def create_asset_file(
    db: Session,
    *,
    asset_id: int,
    filename: str,
    object_key: str,
    file_url: str,
    content_type: Optional[str],
    size: int,
    uploader: Optional[str],
) -> models.AssetFile:
    record = models.AssetFile(
        asset_id=asset_id,
        filename=filename,
        object_key=object_key,
        file_url=file_url,
        content_type=content_type,
        size=size,
        uploader=uploader,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete_asset_file(db: Session, record: models.AssetFile) -> None:
    db.delete(record)
    db.commit()


def list_supplies(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    keyword: Optional[str] = None,
) -> Tuple[int, list[models.SupplyRecord]]:
    stmt = select(models.SupplyRecord)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                models.SupplyRecord.receiver.like(like),
                models.SupplyRecord.item_name.like(like),
                models.SupplyRecord.serial_number.like(like),
            )
        )

    total = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
    page_stmt = (
        stmt.order_by(models.SupplyRecord.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = db.execute(page_stmt).scalars().all()
    return int(total), list(items)


def get_supply(db: Session, supply_id: int) -> Optional[models.SupplyRecord]:
    return db.get(models.SupplyRecord, supply_id)


def get_supply_by_serial(
    db: Session, serial_number: str
) -> Optional[models.SupplyRecord]:
    if not serial_number:
        return None
    return db.execute(
        select(models.SupplyRecord).where(
            models.SupplyRecord.serial_number == serial_number
        )
    ).scalar_one_or_none()


def create_supply(
    db: Session, payload: schemas.SupplyCreate
) -> models.SupplyRecord:
    data = payload.model_dump()
    data["serial_number"] = next_supply_serial(db)
    record = models.SupplyRecord(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_supply(
    db: Session,
    record: models.SupplyRecord,
    payload: schemas.SupplyUpdate,
) -> models.SupplyRecord:
    data = payload.model_dump(exclude_unset=True)
    data.pop("serial_number", None)
    for key, value in data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_supply(db: Session, record: models.SupplyRecord) -> None:
    db.delete(record)
    db.commit()
