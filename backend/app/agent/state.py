from langchain.agents.middleware.types import AgentState as _AgentState


class AgentState(_AgentState):
    """
    Estado del agente conversacional de Vozfi.

    Extiende el `AgentState` de `langchain.agents` (incluye `messages`).
    Punto de extensión para agregar contexto de sesión a futuro (ej: `user_id`).
    """