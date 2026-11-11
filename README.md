# capcut-vlog-edit-skill

A Claude Code skill for editing a YouTube/Instagram vlog inside **CapCut Desktop (Windows)** by driving the app with computer use, safely and without breaking what you already built.

It was written from a real edit (a workday vlog) and records what worked and what failed: backups and read-only verification of the draft JSON, trimming and muting clips, voiceover/music levels, cold open + black dip, hard-cut/punch-in transitions that work offline, tracked face/background blur on a copy of the clip, darkening a small area, titles, and YouTube title/description/tags.

## Contents

```
skills/capcut-vlog-edit/
  SKILL.md              the skill (rules, UI quirks, recipes, checklist)
  scripts/draft_tool.py read-only helper: backup / summary / loudness
```

## Install

Copy the folder into your Claude Code skills directory:

```bash
cp -r skills/capcut-vlog-edit ~/.claude/skills/
```

On Windows: `%USERPROFILE%\.claude\skills\`.

## Requirements

- Windows, CapCut Desktop, Claude Code with computer use enabled
- Python 3 for `draft_tool.py`; ffmpeg (optional, used for loudness checks)

## Notes and limits

- The helper only **reads** CapCut's `draft_content.json` and copies the project folder for backups. It never writes into a draft.
- Many CapCut features (music, effects, transitions, mask shapes) need CapCut's own internet connection; the skill documents offline alternatives.
- UI coordinates and menus change between CapCut versions. Treat the recipes as a guide and verify with a screenshot after each step.
- Always keep a backup and test an effect on one shot before applying it everywhere.

## License

MIT
