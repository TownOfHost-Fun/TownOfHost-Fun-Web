import csv, html
from pathlib import Path
from datetime import datetime

SERVER_ID = "1399723941722853376"

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

tickets = read_csv("tickets.csv")
mods    = read_csv("mod_versions.csv")

# 更新日時
generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

header = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>TownOfHost-Fun Web</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}
    h2 {{ margin-top: 40px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; cursor: pointer; user-select: none; }}
    tr:nth-child(even) {{ background-color: #fafafa; }}
    input, select, label {{ padding: 5px; margin: 10px 10px 10px 0; vertical-align: middle; }}
    .controls {{ margin-bottom: 10px; }}
    .sort-indicator {{ font-size: 0.9em; margin-left: 6px; color: #666; }}
    #modsTable th {{ cursor: default; }}
    .small {{ font-size: 0.9em; color: #555; }}
  </style>
</head>
<body>
<h1>TownOfHost-Fun Web</h1>
<p class="small">最終更新: {generated_time}</p>
"""

tickets_html_start = """
<h2>チケット</h2>
<div class="controls">
  <label for="statusFilter">ステータスで絞り込み：</label>
  <select id="statusFilter" onchange="filterTickets()">
    <option value="">全て</option>
    <option value="open">Open</option>
    <option value="closed">Closed</option>
  </select>

  <label for="titleSearch">タイトルで検索：</label>
  <input type="text" id="titleSearch" onkeyup="filterTickets()" placeholder="タイトルで検索">

  <span class="small">「ID」をクリックして昇順/降順を切り替えることができます</span><br>
  <span class="small">データは最新でない場合があります。</span>
</div>

<table id="ticketsTable">
  <thead>
    <tr>
      <th id="idHeader" onclick="toggleSortById()">ID <span id="idSortIndicator" class="sort-indicator">↑</span></th>
      <th>チャンネル</th>
      <th>ステータス</th>
      <th>タイトル</th>
      <th>バージョン</th>
    </tr>
  </thead>
  <tbody>
"""


tickets_html_rows = ""
for row in tickets:
    channel_id = str(row.get("channel_id",""))
    channel_link = f"https://discord.com/channels/{SERVER_ID}/{channel_id}"
    tickets_html_rows += (
        "    <tr>\n"
        f"      <td>{html.escape(str(row.get('id','')))}</td>\n"
        f"      <td><a target=\"_blank\" href=\"{html.escape(channel_link)}\">{html.escape(channel_id)}</a></td>\n"
        f"      <td>{html.escape(str(row.get('status','')))}</td>\n"
        f"      <td>{html.escape(str(row.get('title','')))}</td>\n"
        f"      <td>{html.escape(str(row.get('version','')))}</td>\n"
        "    </tr>\n"
    )

tickets_html_end = """
  </tbody>
</table>

<script>
var idSortAscending = true;

function parseIdForSort(text) {
  var n = parseInt(text, 10);
  return isNaN(n) ? text.toLowerCase() : n;
}

function toggleSortById() {
  var tbody = document.querySelector("#ticketsTable tbody");
  var rows = Array.from(tbody.querySelectorAll("tr"));
  idSortAscending = !idSortAscending;
  rows.sort(function(a, b) {
    var aId = parseIdForSort(a.cells[0].textContent.trim());
    var bId = parseIdForSort(b.cells[0].textContent.trim());
    if (aId < bId) return idSortAscending ? -1 : 1;
    if (aId > bId) return idSortAscending ? 1 : -1;
    return 0;
  });
  rows.forEach(function(r) { tbody.appendChild(r); });
  document.getElementById("idSortIndicator").textContent = idSortAscending ? "↑" : "↓";
}

function filterTickets() {
  var status = document.getElementById("statusFilter").value.toLowerCase();
  var search = document.getElementById("titleSearch").value.toLowerCase();
  var table = document.getElementById("ticketsTable");
  var trs = table.getElementsByTagName("tr");
  for (var i = 1; i < trs.length; i++) {
    var tds = trs[i].getElementsByTagName("td");
    if (tds.length < 5) { trs[i].style.display = ""; continue; }
    var rowStatus = tds[2].textContent.toLowerCase();
    var rowTitle  = tds[3].textContent.toLowerCase();
    trs[i].style.display = ((status === "" || rowStatus === status) && rowTitle.includes(search)) ? "" : "none";
  }
}

document.addEventListener("DOMContentLoaded", function() {
  try { toggleSortById(); toggleSortById(); } catch (e) {}
});
</script>
"""

mods_html_start = """
<h2>TownOfHost-Fun VersionList</h2>
<div class="controls">
  <label for="versionSearch">バージョン検索：</label>
  <input type="text" id="versionSearch" placeholder="部分文字列で絞り込み" oninput="buildModsTable()">

  <label for="includeBeta"><input type="checkbox" id="includeBeta" checked onchange="buildModsTable()"> β を含める</label>
</div>

<ul id="modsList" style="display:none">
"""

mods_li = ""
for row in mods:
    mods_li += f"  <li>{html.escape(str(row.get('version','')))}</li>\n"

mods_html_end = """</ul>

<div id="modsContainer"></div>

<script>
function extractDigitsArray(ver) {
  var parts = ver.match(/\\d+/g) || [];
  return parts.map(function(p){ return parseInt(p, 10); });
}

function versionHasBeta(ver) {
  return /β|beta/i.test(ver);
}

function compareVersionStrings(a, b) {
  var ap = extractDigitsArray(a);
  var bp = extractDigitsArray(b);
  var len = Math.max(ap.length, bp.length);
  for (var i = 0; i < len; i++) {
    var ai = (i < ap.length) ? ap[i] : 0;
    var bi = (i < bp.length) ? bp[i] : 0;
    if (ai < bi) return -1;
    if (ai > bi) return 1;
  }
  var aBeta = versionHasBeta(a);
  var bBeta = versionHasBeta(b);
  if (aBeta && !bBeta) return 1;
  if (!aBeta && bBeta) return -1;
  return a.localeCompare(b);
}

function buildModsTable() {
  var includeBeta = document.getElementById("includeBeta").checked;
  var filter = document.getElementById("versionSearch").value.toLowerCase();
  var rawLis = Array.from(document.querySelectorAll("#modsList li"));
  var versions = rawLis.map(function(li){ return li.textContent.trim(); }).filter(Boolean);
  versions = versions.filter(function(v) {
    if (!includeBeta && versionHasBeta(v)) return false;
    if (filter && v.toLowerCase().indexOf(filter) === -1) return false;
    return true;
  });

  var groups = {};
  versions.forEach(function(v) {
    var parts = extractDigitsArray(v);
    var major = (parts.length > 0) ? String(parts[0]) : "0";
    if (!groups[major]) groups[major] = [];
    groups[major].push(v);
  });

  var majors = Object.keys(groups).map(function(k){ return parseInt(k,10); }).sort(function(a,b){ return a-b; }).map(String);

  majors.forEach(function(m) {
    groups[m].sort(compareVersionStrings);
  });

  var maxRows = 0;
  majors.forEach(function(m) { if (groups[m].length > maxRows) maxRows = groups[m].length; });

  var container = document.getElementById("modsContainer");
  container.innerHTML = "";

  if (majors.length === 0) {
    container.innerHTML = "<p class=\\"small\\">バージョンが見つかりません。</p>";
    return;
  }

  var table = document.createElement("table");
  table.id = "modsTable";
  var thead = document.createElement("thead");
  var headerRow = document.createElement("tr");
  majors.forEach(function(m) {
    var th = document.createElement("th");
    th.textContent = "Major " + m;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  var tbody = document.createElement("tbody");
  for (var r = 0; r < maxRows; r++) {
    var tr = document.createElement("tr");
    majors.forEach(function(m) {
      var td = document.createElement("td");
      td.textContent = groups[m][r] || "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  }
  table.appendChild(tbody);
  container.appendChild(table);
}

document.addEventListener("DOMContentLoaded", function() {
  buildModsTable();
});
</script>

</body>
</html>
"""


full = (
    header
    + tickets_html_start
    + tickets_html_rows
    + tickets_html_end
    + mods_html_start
    + mods_li
    + mods_html_end
)

out_dir = Path("public")
out_dir.mkdir(exist_ok=True)
(out_dir/"index.html").write_text(full, encoding="utf-8")
print("Generated public/index.html")
