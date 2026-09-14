"""
Schemas Pydantic v2 usados para validar saídas estruturadas do chatbot (Aula 03).
"""
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class PlanoDeEstudo(BaseModel):
    """Plano de estudo estruturado, extraído a partir do pedido do usuário."""

    materia: str = Field(
        description="Matéria ou disciplina que o usuário quer estudar"
    )
    nivel: Literal["iniciante", "intermediario", "avancado"] = Field(
        description="Nível de domínio do usuário sobre o assunto"
    )
    topicos_sugeridos: List[str] = Field(
        description="Lista de tópicos a estudar, em ordem sugerida"
    )
    tempo_estimado_min: int = Field(
        ge=10, le=480, description="Tempo total estimado do plano de estudo, em minutos"
    )
    observacoes: Optional[str] = Field(
        None, description="Dicas de técnica de estudo ou alertas, se houver"
    )
