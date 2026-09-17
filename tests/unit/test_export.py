from fastapi.testclient import TestClient
from app.api.main import app
import zipfile, io, pathlib

def test_export_and_ci():
    p = pathlib.Path("/home/binho/cascudo/fixtures/js-todo")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for f in p.rglob("*"):
            if f.is_file():
                z.write(f, arcname=f.relative_to(p))
    c = TestClient(app)
    r = c.post("/api/push?contribute=true", files={"file": ("a.zip", buf.getvalue(), "application/zip")}, headers={"X-Workspace-Id":"ws-test-export"})
    sid = r.json()["snapshot_id"]
    # export
    for fmt in ["dot","mermaid","svg","md"]:
        e = c.get(f"/api/snapshots/{sid}/export?format={fmt}", headers={"X-Workspace-Id":"ws-test-export"})
        assert e.status_code == 200
        assert "content" in e.json()
    # ci gate should fail on cycle
    ci = c.post("/api/ci", json={"snapshot_id": sid, "fail_on": ["cycle"], "max_cc": 15}, headers={"X-Workspace-Id":"ws-test-export"})
    assert ci.json()["passed"] is False  # js-todo tem ciclo app<->routes
    ci2 = c.post("/api/ci", json={"snapshot_id": sid, "fail_on": [], "max_cc": 100}, headers={"X-Workspace-Id":"ws-test-export"})
    assert ci2.json()["passed"] is True
