"""HTML rendering helpers for the mock attendance portal."""

from __future__ import annotations

from html import escape
from typing import Iterable, Mapping, Optional


def render_units_page(
    day_groups: Iterable[Mapping[str, object]],
    *,
    base_href: str,
) -> str:
    groups = [dict(group) for group in day_groups]
    if not groups:
        groups = [{"anchor": "0", "label": "No sessions available", "entries": []}]

    selected_anchor = str(groups[0]["anchor"])

    option_lines = []
    for group in groups:
        anchor = str(group["anchor"])
        label = str(group["label"])
        selected = ' selected="selected"' if anchor == selected_anchor else ""
        option_lines.append(
            f'            <option value="{escape(anchor)}"{selected}>{escape(label)}</option>'
        )
    options_html = "\n".join(option_lines)

    panel_blocks = []
    for group in groups:
        anchor = str(group["anchor"])
        style_attr = "" if anchor == selected_anchor else ' style="display:none;"'
        entries = [dict(entry) for entry in group.get("entries", [])]
        entry_lines = [
            f'    <div class="dayPanel" id="dayPanel_{escape(anchor)}"{style_attr}>'
        ]
        if not entries:
            entry_lines.append('        <div class="noticeMessage">Nothing on this day</div>')
        else:
            entry_lines.append(
                '        <ul data-role="listview" data-inset="true" class="ui-listview ui-listview-inset ui-corner-all ui-shadow">'
            )
            for idx, entry in enumerate(entries):
                entry = dict(entry)
                classes = ["ui-li-has-icon"]
                if idx == 0:
                    classes.append("ui-first-child")
                if idx == len(entries) - 1:
                    classes.append("ui-last-child")
                status = str(entry.get("status", "pending"))
                status_key = status.lower()
                icon = "tick.png" if status_key == "submitted" else "question.png"
                time_label = escape(str(entry["time_label"]))
                slot_text = f'{escape(str(entry["course_code"]))} {escape(str(entry["slot_label"]))}'
                status_label = {
                    "submitted": "Submitted",
                    "locked": "Closed",
                    "pending": "Open",
                }.get(status_key, status.replace("_", " ").title())
                status_class = {
                    "submitted": "status-submitted",
                    "locked": "status-locked",
                    "pending": "status-open",
                }.get(status_key, "status-open")
                status_html = f'<span class="status-tag {status_class}">{escape(status_label)}</span>'
                if status_key == "submitted":
                    li_classes = classes + ["ui-li-static", "ui-body-inherit"]
                    li_class_str = " ".join(li_classes)
                    entry_lines.append(
                        f'            <li class="{li_class_str}"><img class="ui-li-icon" src="./img/{icon}">{time_label} {slot_text}{status_html}</li>'
                    )
                elif status_key == "locked":
                    li_classes = classes + ["ui-disabled", "ui-li-static", "ui-body-inherit"]
                    li_class_str = " ".join(li_classes)
                    entry_lines.append(
                        f'            <li class="{li_class_str}"><img class="ui-li-icon" src="./img/{icon}">{time_label} {slot_text}{status_html}</li>'
                    )
                else:
                    href = f'Entry.aspx?s={escape(str(entry["session_id"]))}&d={escape(anchor)}'
                    classes_str = " ".join(classes)
                    entry_lines.append(
                        f'            <li class="{classes_str}"><a href="{href}" onclick="$.mobile.loading(\'show\');" class="ui-btn ui-btn-icon-right ui-icon-carat-r"><img class="ui-li-icon" src="./img/{icon}">{time_label} {slot_text}{status_html}</a></li>'
                    )
            entry_lines.append("        </ul>")
        entry_lines.append("    </div>")
        panel_blocks.append("\n".join(entry_lines))
    panels_html = "\n".join(panel_blocks)

    return f"""<!DOCTYPE html>
<html class="ui-mobile">
<head>
    <base href="{escape(base_href)}">
    <title>Choose day and activity</title>
    <meta name="viewport" content="width=device-width, initial-scale=1,maximum-scale=1, user-scalable=no">
    <link rel="stylesheet" href="./jqm/monash.min.css">
    <link rel="stylesheet" href="./jqm/jquery.mobile.icons-1.4.1.min.css">
    <link rel="stylesheet" href="./jqm/jquery.mobile.structure-1.4.1.min.css">
    <link rel="stylesheet" href="./jqm/monash_adjustments.css">
    <script src="./jq/jquery-1.11.0.min.js"></script>
    <script src="./jqm/customPageScript.js"></script>
    <script src="./jqm/jquery.mobile-1.4.1.min.js"></script>

    <style type="text/css">
    #monashLogo {{
        width:325px;
        height:60px;
    }}

    @media only screen and (max-width: 350px) {{
        #monashLogo {{
            width:220px!important;
            height:41px!important;
        }}
    }}

    .status-tag {{
        float:right;
        padding:2px 6px;
        border-radius:12px;
        font-size:0.75em;
        font-weight:bold;
        text-transform:uppercase;
        line-height:1.2;
    }}

    .status-open {{
        background-color:#fff4ce;
        color:#8a6d3b;
    }}

    .status-submitted {{
        background-color:#e6f7ea;
        color:#247f3f;
    }}

    .status-locked {{
        background-color:#f2f2f2;
        color:#707070;
    }}

    .ui-field-contain {{
        display: block !important;
        width: 100% !important;
        clear: both !important;
    }}

    .ui-field-contain label.select {{
        display: block !important;
        width: 100% !important;
        margin-bottom: 8px !important;
        text-align: left !important;
        float: none !important;
        clear: both !important;
        font-weight: bold !important;
    }}

    .ui-field-contain .ui-select,
    .ui-field-contain select {{
        display: block !important;
        width: 100% !important;
        margin-top: 0 !important;
        clear: both !important;
        float: none !important;
    }}
    </style>
</head>
<body class="ui-mobile-viewport ui-overlay-a" style="">

<div data-role="page" data-url="/Student/Units.aspx" tabindex="0" class="ui-page ui-page-theme-a ui-page-footer-fixed ui-page-active" style="padding-bottom: 36px; min-height: 684px;">

    <div id="ctl00_pageHeader" data-role="header" role="banner" class="ui-header ui-bar-inherit">
        <a href="./Default.aspx" id="ctl00_homeButton" data-icon="home" data-theme="b" data-iconpos="notext" class="ui-link ui-btn-left ui-btn ui-btn-b ui-icon-home ui-btn-icon-notext ui-shadow ui-corner-all" data-role="button" role="button">Home</a>
        <h1 style="margin-left: 5%;margin-right: 5%;" class="ui-title" role="heading" aria-level="1"><span id="ctl00_pageHeaderText">Choose day and activity</span></h1>
    </div>

    <div data-role="content" class="ui-content" role="main">

        <div style="margin-bottom:14px; text-align:center;">
            <div style="margin-bottom:8px; font-weight:bold;">Select a day</div>
            <div data-role="fieldcontain" class="ui-field-contain">
                <select id="daySel" data-native-menu="false">
{options_html}
                </select>
            </div>
        </div>

<script>
$(document).ready(function(){{

    function showSelectedPanel(sel)
    {{
        //if provided initial selection which is different to what is selected...
        if(sel!=undefined && $('#daySel').val()!=sel){{
            //$('#daySel option[value='+sel+']').prop("selected", "selected")
            $('#daySel').val(sel);
            $('#daySel').selectmenu('refresh');
        }}

        if(sel==undefined){{
            sel = $('#daySel').val();
        }}

        //hide any existing panel that is visible
        $('.dayPanel').filter(':visible').hide();

        //show the selected panel
        $('#dayPanel_'+sel).show();

        window.location.hash = '#' + sel;
    }}

    showSelectedPanel(window.location.hash && window.location.hash.length>0 ? window.location.hash.replace('#','') : null);

    //register the change handler after first setting the default on page load
    $('#daySel').change(function(){{
        showSelectedPanel();
    }});

}});
</script>

{panels_html}

    </div>

    <div id="ctl00_footer" data-role="footer" data-position="fixed" role="contentinfo" class="ui-footer ui-footer-fixed slideup ui-bar-inherit">
        <div data-role="navbar" class="ui-navbar" role="navigation">
            <ul class="ui-grid-solo">
                <li class="ui-block-a"><a data-role="button" href="SignOut.aspx" class="ui-link ui-btn ui-shadow ui-corner-all" role="button">Logout</a></li>
            </ul>
        </div>
    </div>

</div>

<div class="ui-loader ui-corner-all ui-body-a ui-loader-default"><span class="ui-icon-loading"></span><h1>loading</h1></div>
</body>
</html>"""


def render_entry_page(
    entry: Mapping[str, object],
    *,
    base_href: str,
    day_anchor: Optional[str] = None,
    message: Optional[str] = None,
    error: bool = False,
) -> str:
    status_key = str(entry.get("status", "pending")).lower()
    status = {
        "pending": "Open",
        "locked": "Closed",
        "submitted": "Submitted",
    }.get(status_key, status_key.replace("_", " ").title())
    notice = ""
    if message:
        message_class = "message" if not error else "message error"
        notice = f'<div class="{message_class}">{escape(message)}</div>'

    return f"""<!DOCTYPE html>
<html class="ui-mobile">
<head>
    <base href="{escape(base_href)}">
    <title>Enter code</title>
    <meta name="viewport" content="width=device-width, initial-scale=1,maximum-scale=1, user-scalable=no">
    <link rel="stylesheet" href="./jqm/monash.min.css">
    <link rel="stylesheet" href="./jqm/jquery.mobile.icons-1.4.1.min.css">
    <link rel="stylesheet" href="./jqm/jquery.mobile.structure-1.4.1.min.css">
    <link rel="stylesheet" href="./jqm/monash_adjustments.css">
    <script src="./jq/jquery-1.11.0.min.js"></script>
    <script src="./jqm/customPageScript.js"></script>
    <script src="./jqm/jquery.mobile-1.4.1.min.js"></script>
</head>
<body class="ui-mobile-viewport ui-overlay-a" style="">

<div data-role="page" data-url="/Student/Entry.aspx" tabindex="0" class="ui-page ui-page-theme-a ui-page-footer-fixed ui-page-active" style="padding-bottom: 36px; min-height: 684px;">

    <div id="ctl00_pageHeader" data-role="header" role="banner" class="ui-header ui-bar-inherit">
        <a href="Default.aspx" id="ctl00_homeButton" data-icon="home" data-theme="b" data-iconpos="notext" class="ui-link ui-btn-left ui-btn ui-btn-b ui-icon-home ui-btn-icon-notext ui-shadow ui-corner-all" data-role="button" role="button">Home</a>
        <h1 style="margin-left: 5%;margin-right: 5%;" class="ui-title" role="heading" aria-level="1"><span id="ctl00_pageHeaderText">Enter code</span></h1>
    </div>

    <div data-role="content" class="ui-content" role="main">

        {notice}

        <div style="margin-bottom:14px; text-align:center;">
            <div style="background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;">{escape(str(entry['course_code']))} {escape(str(entry['slot_label']))}</div>
                <div style="font-size: 16px; color: #666; margin-bottom: 10px;">{escape(str(entry['time_label']))}</div>
                <div style="font-size: 14px; color: #888;">Status: {status}</div>
            </div>
        </div>

        <form method="post" data-ajax="false">
            <div data-role="fieldcontain" class="ui-field-contain">
                <label for="ctl00_ContentPlaceHolder1_txtAttendanceCode" class="ui-label">Enter code</label>
                <input type="text" name="ctl00$ContentPlaceHolder1$txtAttendanceCode" id="ctl00_ContentPlaceHolder1_txtAttendanceCode" class="ui-input-text ui-shadow-inset ui-corner-all ui-btn-shadow ui-body-inherit" />
            </div>

            <input type="submit" name="ctl00$ContentPlaceHolder1$btnSubmitAttendanceCode" id="ctl00_ContentPlaceHolder1_btnSubmitAttendanceCode" value="Submit" data-theme="b" class="ui-btn ui-btn-b ui-corner-all ui-shadow">
        </form>

        <div style="margin-top: 10px;">
            <a href="Units.aspx{f'#{day_anchor}' if day_anchor else ''}" data-role="button" class="ui-btn ui-corner-all ui-shadow">Cancel</a>
        </div>

    </div>

    <div id="ctl00_footer" data-role="footer" data-position="fixed" role="contentinfo" class="ui-footer ui-footer-fixed slideup ui-bar-inherit">
        <div data-role="navbar" class="ui-navbar" role="navigation">
            <ul class="ui-grid-solo">
                <li class="ui-block-a"><a data-role="button" href="SignOut.aspx" class="ui-link ui-btn ui-shadow ui-corner-all" role="button">Logout</a></li>
            </ul>
        </div>
    </div>

</div>

<div class="ui-loader ui-corner-all ui-body-a ui-loader-default"><span class="ui-icon-loading"></span><h1>loading</h1></div>
</body>
</html>"""
