"""Auth JWT + workspaces — Codespaces 0GB, multi-tenant."""

from __future__ import annotations

import os
from fastapi import Header, HTTPException

# Para MVP, aceita header opcional X-Workspace-Id ou JWT
# Em prod: Clerk/Auth.js → JWT com workspace_id no claim

DEFAULT_WORKSPACE = "ws-demo"


def get_workspace_id(
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-Id"),
    authorization: str | None = Header(default=None),
) -> str:
    # se JWT presente, valida (stub)
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        # stub: token = workspace_id
        if token.startswith("ws-"):
            return token
        # em prod: decode JWT → workspace_id
        # try: payload = jwt.decode(token, SECRET) -> payload["workspace_id"]
        raise HTTPException(401, "JWT inválido (stub espera ws-*)")
    if x_workspace_id:
        return x_workspace_id
    # Codespaces preview sem auth → ws-demo
    return os.getenv("DEFAULT_WORKSPACE", DEFAULT_WORKSPACE)
