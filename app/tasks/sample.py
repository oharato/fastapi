import asyncio
from app.broker import broker
from app.database import engine
from app.models.job import JobStatus
from app.models.user import User  # noqa: F401 - FK解決のためにインポート必須
from app.services import job as job_service
from sqlmodel import Session


@broker.task
async def run_sample_job(job_id: str, seconds: int = 10) -> str:
    """進捗を更新しながら指定秒数待機するデモタスク。"""
    with Session(engine) as session:
        job_service.update_job_status(session, job_id, JobStatus.running, progress=0)

    steps = max(1, seconds)
    for i in range(1, steps + 1):
        # キャンセルされていたら中断
        with Session(engine) as session:
            job = job_service.get_job(session, job_id)
            if job and job.status == JobStatus.cancelled:
                return "cancelled"

        await asyncio.sleep(1)
        progress = int(i / steps * 100)
        with Session(engine) as session:
            job_service.update_job_status(
                session, job_id, JobStatus.running, progress=progress
            )

    with Session(engine) as session:
        job_service.update_job_status(
            session,
            job_id,
            JobStatus.success,
            result=f"{seconds}秒のジョブが完了しました",
        )
    return "done"
