"""Draw N raw entry-1 variants from the exact served prompt of a run (call 1)."""
import json, re, sys
from factory.infra.ollama import chat

src, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
md = open(src).read()
call1 = md.split("## appel 2")[0]
blocks = re.findall(r"### (system|user)\n\n```\n(.*?)\n```", call1, re.S)
d = dict(blocks)
num_predict = int(re.search(r"num_predict=(\d+)", call1).group(1))
res = []
for k in range(n):
    t, m = chat(d["system"], d["user"], num_predict=num_predict, temperature=0.7)
    res.append({"k": k, "text": t, "done": m.get("done_reason"), "toks": m.get("eval_count")})
    print(k, m.get("done_reason"), m.get("eval_count"), repr(t[:120]), flush=True)
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
