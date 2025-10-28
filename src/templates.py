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
                status = entry.get("status", "pending")
                icon = "tick.png" if status == "submitted" else "question.png"
                time_label = escape(str(entry["time_label"]))
                slot_text = f'{escape(str(entry["course_code"]))} {escape(str(entry["slot_label"]))}'
                if status == "submitted":
                    li_classes = classes + ["ui-li-static", "ui-body-inherit"]
                    entry_lines.append(
                        f'            <li class="{' '.join(li_classes)}"><img class="ui-li-icon" src="./img/{icon}">{time_label} {slot_text}</li>'
                    )
                elif status == "locked":
                    li_classes = classes + ["ui-disabled", "ui-li-static", "ui-body-inherit"]
                    entry_lines.append(
                        f'            <li class="{' '.join(li_classes)}"><img class="ui-li-icon" src="./img/{icon}">{time_label} {slot_text}</li>'
                    )
                else:
                    href = f'Entry.aspx?s={escape(str(entry["session_id"]))}&d={escape(anchor)}'
                    entry_lines.append(
                        f'            <li class="{' '.join(classes)}"><a href="{href}" onclick="$.mobile.loading(\'show\');" class="ui-btn ui-btn-icon-right ui-icon-carat-r"><img class="ui-li-icon" src="./img/{icon}">{time_label} {slot_text}</a></li>'
                    )
            entry_lines.append("        </ul>")
        entry_lines.append("    </div>")
        panel_blocks.append("\n".join(entry_lines))
    panels_html = "\n".join(panel_blocks)

    return f"""<!DOCTYPE html><html class="ui-mobile"><head><base href="{escape(base_href)}"> \
\t<title>Choose day and activity</title> \
\t<meta name="viewport" content="width=device-width, initial-scale=1,maximum-scale=1, user-scalable=no"> \
\t<link rel="stylesheet" href="./jqm/monash.min.css">\n\t<link rel="stylesheet" href="./jqm/jquery.mobile.icons-1.4.1.min.css">\n\t<link rel="stylesheet" href="./jqm/jquery.mobile.structure-1.4.1.min.css">\n\t<link rel="stylesheet" href="./jqm/monash_adjustments.css">\n\t<script src="./jq/jquery-1.11.0.min.js"></script>\n\t<script src="./jqm/customPageScript.js"></script>\n\t<script src="./jqm/jquery.mobile-1.4.1.min.js"></script>\n\t\n\n\t\n\t<style type="text/css">\n\t\n\t#monashLogo \n\t{{\n\t\twidth:325px;\n\t\theight:60px;\n\t}}\n\t\n\t@media only screen and (max-width: 350px) \n\t{{\n\t    #monashLogo \n\t    {{\n\t\t    width:220px!important;\n\t\t    height:41px!important;\n\t    }}\n\t}}\n\t\n\t</style>\n\n    \n\t\n</head> \\n<body class="ui-mobile-viewport ui-overlay-a" style=""> \\n\\n<div data-role="page" data-url="/student/Units.aspx" tabindex="0" class="ui-page ui-page-theme-a ui-page-footer-fixed ui-page-active" style="padding-bottom: 36px; min-height: 684px;">\\n\\n\\t<div id="ctl00_pageHeader" data-role="header" role="banner" class="ui-header ui-bar-inherit">\\n\\t\\t<a href="./Default.aspx" id="ctl00_homeButton" data-icon="home" data-theme="b" data-iconpos="notext" class="ui-link ui-btn-left ui-btn ui-btn-b ui-icon-home ui-btn-icon-notext ui-shadow ui-corner-all" data-role="button" role="button">Home</a>\\n\\t\\t<h1 style="margin-left: 5%;margin-right: 5%;" class="ui-title" role="heading" aria-level="1"><span id="ctl00_pageHeaderText">Choose day and activity</span></h1>\\n\\t</div>\\n\\n\\n\\t<div data-role="content" class="ui-content" role="main">\\t\\n\\n        \\n\\t\\n\\t    \\n\\n<div style="text-align:center;color:#909090;margin-bottom:14px;"><span id="ctl00_ContentPlaceHolder1_userName">Mock Student</span></div>\\n\\n<script>\\n\\n$(document).ready(function(){{\\n\\n    function showSelectedPanel(sel)\\n    {{\\n   \\n            //if provided initial selection which is different to what is selected...\\n            if(sel!=undefined && $('#daySel').val()!=sel){{\\n                //$('#daySel option[value='+sel+']').prop("selected", "selected")\\n                $('#daySel').val(sel);\\n                $('#daySel').selectmenu('refresh');\\n            }}\\n            \\n            if(sel==undefined){{\\n                sel = $('#daySel').val();\\n            }}\\n    \\n            //hide any existing panel that is visible\\n            $('.dayPanel').filter(':visible').hide();\\n    \\n            //show the selected panel\\n            $('#dayPanel_'+sel).show();    \\n            \\n            window.location.hash = '#' + sel;\\n    }}\\n\\n    showSelectedPanel(window.location.hash.length>0?window.location.hash.replace('#',''):undefined);\\n\\n    //register the change handler after first setting the default on page load  \\n    $('#daySel').change(function(){{\\n        showSelectedPanel();\\n    }});    \\n\\n}});\\n\\n</script>\\n\\n    <div data-role="fieldcontain" class="ui-field-contain">\\n        <label for="daySel" class="select">Select a day</label>\\n        <select id="daySel" data-native-menu="false">\\n{options_html}\\n        </select>\\n    </div>\\n\\n{panels_html}\\n\\n\\n\\t</div>\\n\\n    <div id="ctl00_footer" data-role="footer" data-position="fixed" role="contentinfo" class="ui-footer ui-footer-fixed slideup ui-bar-inherit">\\n\\t\\t<div data-role="navbar" class="ui-navbar" role="navigation">\\n\\t\\t\\t<ul class="ui-grid-solo">\\n\\t\\t\\t\\t<li class="ui-block-a"><a data-role="button" href="SignOut.aspx" class="ui-link ui-btn ui-shadow ui-corner-all" role="button">Logout</a></li>\\n\\t    \\t</ul>\\n\\t\\t</div>\\n\\t</div>\\n\\n</div>\\n\\n\\n\\n<div class="ui-loader ui-corner-all ui-body-a ui-loader-default"><span class="ui-icon-loading"></span><h1>loading</h1></div></body></html>"""


def render_entry_page(
    entry: Mapping[str, object],
    *,
    base_href: str,
    message: Optional[str] = None,
    error: bool = False,
) -> str:
    status = str(entry.get("status", "pending")).capitalize()
    notice = ""
    if message:
        banner_class = "ui-body-b" if not error else "ui-body-a"
        notice = (
            f'<div class="{banner_class} ui-corner-all" style="padding:12px;margin-bottom:12px;">'
            f"{escape(message)}</div>"
        )

    return f"""<!DOCTYPE html><html class="ui-mobile"><head><base href="{escape(base_href)}">
<title>Submit attendance code</title>
<meta name="viewport" content="width=device-width, initial-scale=1,maximum-scale=1, user-scalable=no">
<link rel="stylesheet" href="./jqm/monash.min.css">
<link rel="stylesheet" href="./jqm/jquery.mobile.icons-1.4.1.min.css">
<link rel="stylesheet" href="./jqm/jquery.mobile.structure-1.4.1.min.css">
<link rel="stylesheet" href="./jqm/monash_adjustments.css">
<script src="./jq/jquery-1.11.0.min.js"></script>
<script src="./jqm/jquery.mobile-1.4.1.min.js"></script>
</head>
<body class="ui-mobile-viewport ui-overlay-a" style="">
<div data-role="page" data-url="/student/Entry.aspx" tabindex="0" class="ui-page ui-page-theme-a ui-page-footer-fixed ui-page-active" style="padding-bottom: 36px; min-height: 684px;">
    <div data-role="header" role="banner" class="ui-header ui-bar-inherit">
        <a href="Units.aspx" data-icon="back" data-theme="b" class="ui-link ui-btn ui-btn-b ui-icon-back ui-btn-icon-left ui-shadow ui-corner-all" data-role="button" role="button">Back</a>
        <h1 class="ui-title" role="heading" aria-level="1"><span id="ctl00_pageHeaderText">Submit attendance code</span></h1>
    </div>

    <div data-role="content" class="ui-content" role="main">
{notice}
        <div class="ui-body ui-body-inherit ui-corner-all" style="margin-bottom:12px;">
            <p><strong>Course:</strong> {escape(str(entry['course_code']))}</p>
            <p><strong>Activity:</strong> {escape(str(entry['slot_label']))}</p>
            <p><strong>Scheduled:</strong> {escape(str(entry['time_label']))}</p>
            <p><strong>Status:</strong> {escape(status)}</p>
        </div>
        <form method="post" data-ajax="false">
            <div class="ui-field-contain">
                <label for="ctl00_ContentPlaceHolder1_txtAttendanceCode">Attendance code</label>
                <input type="text" name="ctl00$ContentPlaceHolder1$txtAttendanceCode" id="ctl00_ContentPlaceHolder1_txtAttendanceCode" />
            </div>
            <input type="submit" name="ctl00$ContentPlaceHolder1$btnSubmitAttendanceCode" id="ctl00_ContentPlaceHolder1_btnSubmitAttendanceCode" value="Submit code" data-theme="b">
        </form>
    </div>

    <div data-role="footer" class="ui-footer ui-bar-inherit ui-footer-fixed">
        <h4>Always Attend Mock Portal</h4>
    </div>
</div>
</body></html>"""
