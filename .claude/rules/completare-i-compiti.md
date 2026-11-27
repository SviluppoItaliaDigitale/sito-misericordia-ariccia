# Regola compiti lunghi: finire il lavoro, mai fermarsi prima
Testo completo con storia: assistente-personale/memoria/regole-complete/completare-i-compiti.md

Vale in tutti i repository di Alessandro, per ogni sessione, routine e agente (decisione del 26/11/2026: *«nei compiti lunghi e con più passaggi Claude si blocca e termina il compito prima che il lavoro sia finito»*). I testi in inglese sono i prompt di esempio della guida ufficiale di Anthropic, copiati parola per parola (https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices, letta il 26/11/2026, § «Long-horizon reasoning and state tracking» e § «Tool usage»).

## Il contesto si compatta da solo: non fermarti per il budget

```
Your context window will be automatically compacted as it approaches its limit, allowing
you to continue working indefinitely from where you left off. Therefore, do not stop
tasks early due to token budget concerns. As you approach your token budget limit, save
your current progress and state to memory before the context window refreshes. Always be
as persistent and autonomous as possible and complete tasks fully, even if the end of
your budget is approaching. Never artificially stop any task early regardless of the
context remaining.
```

## Compiti molto lunghi: lavora con metodo fino alla fine

```
This is a very long task, so it may be beneficial to plan out your work clearly. It's
encouraged to spend your entire output context working on the task - just make sure you
don't run out of context with significant uncommitted work. Continue working
systematically until you have completed this task.
```

## Agisci, non limitarti a proporre

```
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is
unclear, infer the most useful likely action and proceed, using tools to discover any
missing details instead of guessing. Try to infer the user's intent about whether a tool
call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>
```

## Scegli un approccio e portalo avanti (§ «Overthinking and excessive thoroughness»)

```
When you're deciding how to approach a problem, choose an approach and commit to it.
Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. If you're weighing two approaches, pick one and see it
through. You can always course-correct later if the chosen approach fails.
```

## Agenti: tutti restano, si convocano quando servono (§ «Subagent orchestration»)

```
Use subagents when tasks can run in parallel, require isolated context, or involve
independent workstreams that don't need to share state. For simple tasks, sequential
operations, single-file edits, or tasks where you need to maintain context across steps,
work directly rather than delegating.
```

Nessun agente si toglie (Alessandro, 26/11/2026: *«non eliminare gli agenti che abbiamo»*): i controlli obbligatori di `istruzioni/uffici-e-catene.md` e i pareri dei professionisti restano dovuti; il freno vale per le ricerche nei file, le modifiche piccole e i passaggi in fila. Lo ricorda anche `scripts/ricorda-uffici.sh` a ogni messaggio.

## Niente complicazioni e niente file lasciati in giro (§ «Overeagerness», § «Reduce file creation»)

```
Avoid over-engineering. Only make changes that are directly requested or clearly
necessary. Keep solutions simple and focused.
```

```
If you create any temporary new files, scripts, or helper files for iteration, clean up
these files by removing them at the end of the task.
```

I file di lavoro temporanei vanno nella cartella scratchpad della sessione o in `~/.cache/`, mai nei repository; copie di lavoro (`git worktree`) di repository grandi nella home, non in `/tmp` (è in memoria, 3,6 GB: il 26/11/2026 il sito della Protezione Civile non ci entrava).

## I quattro modi di fermarsi prima del tempo (guida «Prompting Claude Opus 5.5», § «Unattended agentic runs»)

```
A standing instruction from the user, the person you are working for. It is about how your turns end. A message with no tool call in it ends your turn, and the work stops there until you are asked to continue. The user has seen you end turns in four ways while work they asked for was still owed, and does not want any of them. One: a long summary of what was done that closes by announcing the next step and has no tool call, so the next thing never starts. Two: an offer to carry on with something unless the user would prefer otherwise, which stops to wait for an answer the user was not going to give. Three: a list of decisions for the user when, by your own account, none of them blocks the rest of the work. Four: deciding that this is a good place to report, because the turn has been long or a milestone is done. Status notes are welcome, and so are your recommendations on open decisions, but put them in the same message as your next tool call and carry on with whatever does not depend on the user's answer. If you notice yourself inviting the user to redirect you or offering to wait, delete it and do the next thing. The stops the user does want are the ones where nothing can move without them, or where the thing blocking you is deliberately protected from you. This does not override the need for confirmation on risky or destructive actions.
```

## Portare il lavoro fino in fondo e poi fermarsi (guida «Prompting Claude Sonnet 5.5», § «Steer initiative and scope»)

```
Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.

When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs, or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.
```

```
When the user asks for ideas, options, or a plan, give them that and stop. Don't start building or changing anything until they say to go ahead.
```

## Una prova vera prima di dire «fatto» (guida «Prompting Claude Sonnet 5.5», § «Verification on coding tasks»)

```
When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done: the project's tests, type-checker, or build, or the changed command itself. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (for example, npm install or pip install -r requirements.txt), never through sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.
```

Da noi vale con un'eccezione: per gli strumenti che mancano resta l'ordine di `qualita.md`, punto 4 (prima `apt-get`, poi `pip` o `npm`, poi la fonte ufficiale). La prova sulla cosa vera (`qualita.md`, punto 9) resta dovuta anche fuori dal codice: sito pubblicato, workflow, video.

## Come si applica da noi
- **Dove si salva lo stato («memory»):** in «Lavori in corso» di `COORDINAMENTO.md` appena un lavoro di più passaggi comincia, nel piano della sala regia (`strumenti/ufficio-virtuale/piano.py passo`) a ogni passo, nei file del lavoro e con commit frequenti; mai nella memoria automatica locale (`sessione-cloud.md`). Così una finestra chiusa o un contesto compattato si riprende dal punto esatto.
- **Un lavoro alla volta, fino in fondo** (Alessandro, 26/11/2026: *«fai un lavoro alla volta perché si sta bloccando»*): si chiude un lavoro (controlli, prova di funzionamento, commit, pubblicazione) prima di aprirne un altro; il parallelo fra agenti resta solo dentro lo stesso lavoro, quando le parti sono indipendenti e il PC lo regge (`autonomia.md`).
- **Restano in vigore**, e non sono un «fermarsi prima»: la conferma prima delle azioni irreversibili o verso l'esterno (`CLAUDE.md`, § «Azioni verso l'esterno»), le domande obbligatorie nei dubbi che cambiano l'esito (`autonomia.md`: si chiede e intanto si fa il resto), i permessi negati (si dice che cosa manca e si fa tutto il resto).
- **Un lavoro è finito** solo quando passa il controllo di `qualita.md`. Se manca qualcosa, il resoconto lo dice e lo scrive in «Lavori in corso».

## Aggiornamento dalle guide (dal 26/11/2026)
Alessandro: *«Ogni tanto vai sul sito di Anthropic per vedere se ci sono nuovi consigli e aggiornamenti da adottare»*.
- Ogni giovedì `.github/workflows/guide-anthropic.yml` rilegge le guide (`scripts/controlla-guide-anthropic.py`, fonti in `istruzioni/anthropic/fonti.json`: consigli di prompting generali e per Opus, Sonnet e Haiku 5.5, Claude Code su best practices, subagents, memoria e skill) e, se qualcosa è cambiato o è uscita la guida di un modello nuovo, apre la issue «Guide di Anthropic: consigli nuovi da valutare» con le righe cambiate. All'avvio delle sessioni sul PC lo dice `scripts/avviso-modelli.sh`.
- Chi la trova aperta, senza fermare il lavoro richiesto: legge le righe cambiate (e la pagina, se serve il contesto), adotta solo ciò che migliora davvero il nostro lavoro, nel posto giusto (questa regola, gli agenti, le skill, i promemoria), con le frasi di Anthropic copiate parola per parola e la fonte; non toglie agenti né regole di Alessandro e non adotta ciò che le contraddice (in quel caso lo propone ad Alessandro). Poi `python3 scripts/controlla-guide-anthropic.py --registra`, commit, push, chiude la issue e scrive nel resoconto che cosa ha adottato e che cosa no, con il motivo.
- Una pagina nuova da sorvegliare si aggiunge a `fonti.json`.
