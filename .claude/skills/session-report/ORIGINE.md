# Origine

Copia senza modifiche dal catalogo ufficiale dei plugin di Claude Code: github.com/anthropics/claude-plugins-official (Anthropic, licenza Apache 2.0, testo in LICENSE accanto). Plugin di origine: session-report (commit 0412be76f50a), claude-md-management 1.0.0, security-guidance 2.0.18; copiata il 07/11/2026.

Sta nel repository perché le sessioni cloud (app, routine) non installano i plugin dichiarati nelle impostazioni del repository, ma leggono skill, comandi e hook del repository (memoria/plugin-nel-cloud.md di assistente-personale). Sul PC session-report e claude-md-management non sono installati come plugin; security-guidance resta plugin (riceve l'accesso all'account per le revisioni) e questi hook partono solo nel cloud (`CLAUDE_CODE_REMOTE=true`). Per aggiornarla: ricopiare dalla stessa fonte in tutti i repository insieme.
