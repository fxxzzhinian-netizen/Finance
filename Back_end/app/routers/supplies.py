"""物资领取记录 API 路由。"""
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from .. import activity, crud, models, schemas
from ..config import get_settings
from ..database import get_db
from ..qrcode_util import make_qr_png
from ..security import get_current_user

router = APIRouter(
    prefix="/api/supplies",
    tags=["物资管理"],
    dependencies=[Depends(get_current_user)],
)


def _build_supply_qr_url(serial_number: str) -> str:
    settings = get_settings()
    base = settings.public_base_url.rstrip("/")
    return f"{base}/p/supply/{quote(serial_number)}"


@router.get("", response_model=schemas.SupplyListOut, summary="物资领取记录分页查询")
def list_supplies(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=200, description="每页数量"),
    keyword: Optional[str] = Query(None, description="按领取人/物品/序列号模糊搜索"),
    db: Session = Depends(get_db),
):
    total, items = crud.list_supplies(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
    )
    return {"total": total, "items": items}


@router.get(
    "/next-serial",
    response_model=schemas.SupplyNextSerialOut,
    summary="预览下一条物资序列号",
)
def next_supply_serial(db: Session = Depends(get_db)):
    return {"serial_number": crud.next_supply_serial(db)}


@router.get("/{supply_id}", response_model=schemas.SupplyOut, summary="物资领取记录详情")
def get_supply(supply_id: int, db: Session = Depends(get_db)):
    record = crud.get_supply(db, supply_id)
    if not record:
        raise HTTPException(status_code=404, detail="物资记录不存在")
    return record


@router.get(
    "/{supply_id}/qrcode-info",
    response_model=schemas.SupplyQrInfoOut,
    summary="获取该物资记录的二维码信息（URL + 图片接口）",
)
def supply_qr_info(supply_id: int, db: Session = Depends(get_db)):
    record = crud.get_supply(db, supply_id)
    if not record:
        raise HTTPException(status_code=404, detail="物资记录不存在")
    return {
        "serial_number": record.serial_number,
        "qr_url": _build_supply_qr_url(record.serial_number),
        "image_url": f"/api/supplies/{record.id}/qrcode.png",
    }


@router.get(
    "/{supply_id}/qrcode.png",
    summary="下载该物资记录的二维码 PNG 图片",
    responses={200: {"content": {"image/png": {}}}},
)
def supply_qrcode_png(supply_id: int, db: Session = Depends(get_db)):
    record = crud.get_supply(db, supply_id)
    if not record:
        raise HTTPException(status_code=404, detail="物资记录不存在")
    png = make_qr_png(_build_supply_qr_url(record.serial_number), box_size=10, border=2)
    headers = {
        "Content-Disposition": f'inline; filename="supply-{record.serial_number}.png"',
        "Cache-Control": "no-store",
    }
    return Response(content=png, media_type="image/png", headers=headers)


@router.post(
    "",
    response_model=schemas.SupplyOut,
    status_code=status.HTTP_201_CREATED,
    summary="新增物资领取记录",
)
def create_supply(
    payload: schemas.SupplyCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    record = crud.create_supply(db, payload)
    after = activity.supply_to_dict(record)
    changes = activity.diff_supply({}, after)
    activity.log(
        db,
        action="supply.create",
        actor=current_user,
        target_type="supply",
        target_id=record.id,
        target_label=record.serial_number,
        summary=f"新增物资记录：{record.receiver} 领取 {record.item_name} x{record.quantity}",
        changes=changes,
        request=request,
    )
    return record


@router.put("/{supply_id}", response_model=schemas.SupplyOut, summary="更新物资领取记录")
def update_supply(
    supply_id: int,
    payload: schemas.SupplyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    record = crud.get_supply(db, supply_id)
    if not record:
        raise HTTPException(status_code=404, detail="物资记录不存在")
    before = activity.supply_to_dict(record)
    record = crud.update_supply(db, record, payload)
    after = activity.supply_to_dict(record)
    changes = activity.diff_supply(before, after)
    if changes:
        if len(changes) == 1:
            summary = f"修改物资记录 {record.serial_number} 的「{changes[0]['label']}」"
        else:
            summary = f"修改物资记录 {record.serial_number}（共 {len(changes)} 项变更）"
        activity.log(
            db,
            action="supply.update",
            actor=current_user,
            target_type="supply",
            target_id=record.id,
            target_label=record.serial_number,
            summary=summary,
            changes=changes,
            request=request,
        )
    return record


@router.delete(
    "/{supply_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除物资领取记录",
)
def delete_supply(
    supply_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    record = crud.get_supply(db, supply_id)
    if not record:
        raise HTTPException(status_code=404, detail="物资记录不存在")
    record_id = record.id
    serial_number = record.serial_number
    summary = f"删除物资记录：{record.receiver} 领取 {record.item_name} x{record.quantity}"
    crud.delete_supply(db, record)
    activity.log(
        db,
        action="supply.delete",
        actor=current_user,
        target_type="supply",
        target_id=record_id,
        target_label=serial_number,
        summary=summary,
        request=request,
    )
    return None
