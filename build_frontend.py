"""Transform LibraryAI-Pro-Light-Readable.html into API-integrated frontend/index.html"""
import re
from pathlib import Path

root = Path(__file__).parent
src = root / "LibraryAI-Pro-Light-Readable.html"
dst = root / "frontend" / "index.html"

content = src.read_text(encoding="utf-8")

start = content.find("//  STANDALONE MOCK BACKEND")
end = content.find("//  HELPERS")
if start == -1 or end == -1:
    raise SystemExit(f"Could not find mock backend markers: start={start}, end={end}")

content = content[:start] + content[end:]

header = """<script src="js/api.js?v=2"></script>
<script>
'use strict';
let ROLE=null, CU={};
let trendInst,genreInst,statusInst;
const GC={'Technology':'#1a6b5a','Science':'#4a2d8e','Literature':'#b84020','History':'#c9893a','Fiction':'#1a4a8e','Self-Help':'#2a6b2a','Mathematics':'#6b4a00','Philosophy':'#4a0000','Biography':'#004a4a'};
const GE={'Technology':'💻','Science':'🔬','Literature':'📜','History':'🏛','Fiction':'🚀','Self-Help':'🌱','Mathematics':'∑','Philosophy':'🧠','Biography':'👤'};

"""

content = re.sub(
    r"<script>\s*\n'use strict';\s*\n// ═+",
    header + "// ═",
    content,
    count=1,
)

content = content.replace(
    "const r=await post('/student/login',{member_id:id,password:pw});\n    CU=r.student; startApp('student');",
    "const r=await post('/student/login',{member_id:id,password:pw});\n    setToken(r.access_token);\n    CU=r.student; startApp('student');",
)

content = content.replace(
    "const r=await post('/admin/login',{username:u,password:p});\n    CU=r.admin; startApp('admin');",
    "const r=await post('/admin/login',{username:u,password:p});\n    setToken(r.access_token);\n    CU=r.admin; startApp('admin');",
)

content = content.replace(
    "function logout(){\n  ROLE=null;CU={};",
    "function logout(){\n  clearToken();\n  ROLE=null;CU={};",
)

# Route dashboard calls through analytics endpoint alias
content = content.replace("get('/dashboard')", "get('/analytics/dashboard')")

dst.write_text(content, encoding="utf-8")
print(f"Wrote {dst} ({len(content.splitlines())} lines)")
