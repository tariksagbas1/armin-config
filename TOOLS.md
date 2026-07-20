# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Python-Based Skills

Before running a skill that uses Python:

1. Check the skill directory for `.venv`.
2. If `.venv` does not exist, create it with `python3 -m venv .venv`.
3. If the skill has `requirements.txt`, install it with
   `.venv/bin/python -m pip install -r requirements.txt`.
4. Activate the environment and run the skill in the same shell command,
   because activation does not persist across separate shell calls:
   `source .venv/bin/activate && python <script> <arguments>`.

Run these commands from the skill directory unless its `SKILL.md` says
otherwise.

## Related

- [Agent workspace](/concepts/agent-workspace)
