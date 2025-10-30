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


def normalized_student_base_href(request: web.Request) -> str:
    base_href = str(request.url.with_query(None))
    if "/student/" in base_href:
        base_href = base_href.replace("/student/", "/Student/", 1)
    return base_href


async def units_handler(request: web.Request) -> web.Response:
    model: Model = request.app["model"]
    groups = day_groups(model)
    base_href = normalized_student_base_href(request)
    html = render_units_page(groups, base_href=base_href)
    return web.Response(text=html, content_type="text/html")


async def entry_handler(request: web.Request) -> web.Response:
    session_id = request.query.get("s") or request.query.get("session")
    day_anchor = request.query.get("d")
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
    base_href = normalized_student_base_href(request)
    html = render_entry_page(entry_map, base_href=base_href, day_anchor=day_anchor, message=message, error=error)
    return web.Response(text=html, content_type="text/html")


async def reset_handler(request: web.Request) -> web.Response:
    data_path: Path = request.app["data_path"]
    request.app["model"] = load_model(data_path)
    return web.json_response({"status": "ok"})


async def attendance_info_handler(request: web.Request) -> web.Response:
    """Handler for /student/AttendanceInfo.aspx - returns enrolled course codes."""
    model: Model = request.app["model"]

    # Extract unique course codes from the model
    course_codes = set()
    for day in model.days:
        for entry in day.entries:
            course_codes.add(entry.course_code)

    # Create a simple HTML page with course codes that submit.py can scrape
    course_codes_list = sorted(list(course_codes))
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Attendance Information</title>
</head>
<body>
    <h1>Enrolled Courses</h1>
    <div>
        {' '.join(course_codes_list)}
    </div>
</body>
</html>"""

    return web.Response(text=html, content_type="text/html")


def create_app(data_path: Path = DEFAULT_JSON) -> web.Application:
    app = web.Application()
    app["data_path"] = data_path
    app["model"] = load_model(data_path)

    async def home_handler(request: web.Request) -> web.Response:
        """Main student portal homepage with two main options"""
        base_href = normalized_student_base_href(request)
        html = f"""<!DOCTYPE html>
<html class="ui-mobile">
<head>
    <base href="{base_href}">
    <title>Attendance</title>
    <meta name="viewport" content="width=device-width, initial-scale=1,maximum-scale=1, user-scalable=no">
    <link rel="stylesheet" href="./jqm/monash.min.css">
    <link rel="stylesheet" href="./jqm/jquery.mobile.icons-1.4.1.min.css">
    <link rel="stylesheet" href="./jqm/jquery.mobile.structure-1.4.1.min.css">
    <link rel="stylesheet" href="./jqm/monash_adjustments.css">
    <script src="./jq/jquery-1.11.0.min.js"></script>
    <script src="./jqm/jquery.mobile-1.4.1.min.js"></script>
</head>
<body class="ui-mobile-viewport ui-overlay-a">
<div data-role="page" class="ui-page ui-page-theme-a ui-page-footer-fixed ui-page-active">
    <div data-role="header" role="banner" class="ui-header ui-bar-inherit">
        <h1 class="ui-title" role="heading" aria-level="1">Attendance</h1>
    </div>

    <div data-role="content" class="ui-content" role="main">
        <div style="text-align:center;color:#909090;margin-bottom:14px;">Mock Student</div>

        <div style="margin-bottom:20px;">
            <a href="Units.aspx" data-role="button" data-ajax="false" class="ui-btn ui-btn-b ui-corner-all">Enter attendance code</a>
        </div>

        <div style="margin-bottom:20px;">
            <a href="AttendanceInfo.aspx" data-role="button" class="ui-btn ui-corner-all">Attendance by unit</a>
        </div>
    </div>

    <div data-role="footer" class="ui-footer ui-bar-inherit ui-footer-fixed">
        <div data-role="navbar" class="ui-navbar" role="navigation">
            <ul class="ui-grid-solo">
                <li class="ui-block-a"><a data-role="button" href="SignOut.aspx" class="ui-link ui-btn ui-shadow ui-corner-all" role="button">Logout</a></li>
            </ul>
        </div>
    </div>
</div>
</body>
</html>"""
        return web.Response(text=html, content_type="text/html")

    async def redirect_to_student(request: web.Request) -> web.Response:
        raise web.HTTPFound("/student/")

    app.add_routes(
        [
            web.get("/", redirect_to_student),
            web.get("/student/", home_handler),
            web.get("/student", redirect_to_student),
            web.get("/Student/", home_handler),
            web.get("/Student", redirect_to_student),
            web.get("/student/Units.aspx", units_handler),
            web.get("/Student/Units.aspx", units_handler),
            web.get("/student/Entry.aspx", entry_handler),
            web.get("/Student/Entry.aspx", entry_handler),
            web.post("/student/Entry.aspx", entry_handler),
            web.post("/Student/Entry.aspx", entry_handler),
            web.get("/student/AttendanceInfo.aspx", attendance_info_handler),
            web.get("/Student/AttendanceInfo.aspx", attendance_info_handler),
            web.get("/student/Default.aspx", home_handler),
            web.get("/Student/Default.aspx", home_handler),
            web.post("/mock/reset", reset_handler),
        ]
    )

    if STATIC_ROOT.exists():
        for prefix in ("student", "Student"):
            base = f"/{prefix}"
            app.router.add_static(f"{base}/jq/", str(STATIC_ROOT / "jq"))
            app.router.add_static(f"{base}/jqm/", str(STATIC_ROOT / "jqm"))
            app.router.add_static(f"{base}/img/", str(STATIC_ROOT / "img"))
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
