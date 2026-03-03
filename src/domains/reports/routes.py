from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...authentication import CurrentUser
from ...database import retrieve_database
from . import excel_service, pdf_service

router = APIRouter(prefix="/inventories/{inventory_id}/reports", tags=["reports"])

DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]


@router.get(
    "/pdf",
    summary="Download PDF report",
    description="Generates and downloads the GHG inventory report as a PDF file.",
)
async def download_pdf_report(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    content = await pdf_service.generate_pdf(inventory_id, session)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=inventario-{inventory_id}.pdf"
        },
    )


@router.get(
    "/excel",
    summary="Download Excel report",
    description="Generates and downloads the GHG inventory report as an Excel file.",
)
async def download_excel_report(
    inventory_id: UUID,
    current_user: CurrentUser,
    session: DatabaseSession,
):
    content = await excel_service.generate_excel(inventory_id, session)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=inventario-{inventory_id}.xlsx"
        },
    )
