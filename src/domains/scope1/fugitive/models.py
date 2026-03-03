from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ....base import Base


class EmissaoFugitiva(Base):
    __tablename__ = "emissoes_fugitivas"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organizacao_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizacoes.id", ondelete="SET NULL"), index=True)
    gas: Mapped[str] = mapped_column(String(100), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    gwp_value: Mapped[float] = mapped_column(Float, nullable=False)
    emissoes_tco2e: Mapped[float] = mapped_column(Float, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow)
