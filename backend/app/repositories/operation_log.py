from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog


def create_log(db: Session, operator: str, action: str, target: str = None, detail: str = None):
    log = OperationLog(operator=operator, action=action, target=target, detail=detail)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_logs(db: Session, page: int, page_size: int):
    total = db.execute(select(func.count(OperationLog.id))).scalar()

    stmt = (
        select(OperationLog)
        .order_by(OperationLog.id.desc())
        .limit(page_size)
        .offset((page - 1) * page_size)
    )
    logs = db.execute(stmt).scalars().all()

    return {
        "total": total,
        "items": [
            {
                "id": l.id,
                "operator": l.operator,
                "action": l.action,
                "target": l.target,
                "detail": l.detail,
                "created_at": l.created_at,
            }
            for l in logs
        ]
    }
