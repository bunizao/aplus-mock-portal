"""JSON-backed mock portal server."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from aiohttp import web

from . import PACKAGE_ROOT
from .data_loader import Model, day_groups, find_entry, load_model
from .templates import render_entry_page, render_units_page

STATIC_ROOT = PACKAGE_ROOT.parent / "static"
DEFAULT_JSON = PACKAGE_ROOT.parent / "mock_units.json"


async def units_handler(request: web.Request) -> web.Response:
    model: Model = request.app["model"]
    groups = day_groups(model)
    base_href = str(request.url.with_query(None))
    html = render_units_page(groups, base_href=base_href)
    return web.Response(text=html, content_type="text/html")


async def entry_handler(request: web.Request) -> web.Response:
    session_id = request.query.get("s") or request.query.get("session")
    if not session_id:
        raise web.HTTPBadRequest(text="Missing session id")
    model: Model = request.app["model"]
    message: Optional[str] = None
    error = False

    if request.method == "POST":
        form = await request.post()
        code = form.get("ctl00$ContentPlaceHolder1$txtAttendanceCode", "")
        found = find_entry(model, session_id)
        if found is None:
            raise web.HTTPNotFound(text="Session not found")
        _, entry = found
        ok = False
        if entry.status == "submitted":
            ok = True
        elif entry.status == "locked":
            ok = False
        else:
            ok = entry.code.strip().upper() == (code or "").strip().upper()
            if ok:
                entry.status = "submitted"
        if ok:
            message = "Code submitted successfully."
        else:
            message = "Invalid code. Please try again."
            error = True

    found = find_entry(model, session_id)
    if found is None:
        raise web.HTTPNotFound(text="Session not found")
    _, entry = found
    entry_map = {
        "course_code": entry.course_code,
        "slot_label": entry.slot_label,
        "time_label": entry.time_label,
        "status": entry.status,
    }
    base_href = str(request.url.with_query(None))
    html = render_entry_page(entry_map, base_href=base_href, message=message, error=error)
    return web.Response(text=html, content_type="text/html")


async def reset_handler(request: web.Request) -> web.Response:
    data_path: Path = request.app["data_path"]
    request.app["model"] = load_model(data_path)
    return web.json_response({"status": "ok"})


def create_app(data_path: Path = DEFAULT_JSON) -> web.Application:
    app = web.Application()
    app["data_path"] = data_path
    app["model"] = load_model(data_path)

    async def redirect_to_units(request: web.Request) -> web.Response:
        raise web.HTTPFound("/student/Units.aspx")

    app.add_routes(
        [
            web.get("/", redirect_to_units),
            web.get("/student/", redirect_to_units),
            web.get("/student/Units.aspx", units_handler),
            web.get("/student/Entry.aspx", entry_handler),
            web.post("/student/Entry.aspx", entry_handler),
            web.post("/mock/reset", reset_handler),
        ]
    )

    if STATIC_ROOT.exists():
        app.router.add_static("/student/jq/", str(STATIC_ROOT / "jq"))
        app.router.add_static("/student/jqm/", str(STATIC_ROOT / "jqm"))
        app.router.add_static("/student/img/", str(STATIC_ROOT / "img"))
        app.router.add_static("/static/", str(STATIC_ROOT), show_index=True)
    else:
        raise FileNotFoundError(f"Missing static assets at {STATIC_ROOT}")
    return app


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the APLUS mock portal server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--data", type=Path, default=DEFAULT_JSON, help="Path to mock JSON dataset")
    args = parser.parse_args(argv)

    app = create_app(args.data)
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
