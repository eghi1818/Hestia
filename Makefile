.PHONY: gate pack resume smoke

gate:
	@bash tools/gate.sh

pack:
	@bash tools/handoff_pack.sh

resume:
	@bash tools/resume.sh

smoke:
	@curl -s -o /dev/null -w "http %{http_code}\n" --max-time 3 http://127.0.0.1:8787/ || true
newchat:
	bash tools/siapkan_newchat.sh --naik
