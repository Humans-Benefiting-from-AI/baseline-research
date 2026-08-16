# Copilot Instructions

## End-of-Session Summary

At the end of every session — whether the user explicitly closes it, says they're done, or signals they're wrapping up — proactively provide a structured summary without being asked. Use this format:

**Session Summary**
- **What we accomplished:** Brief bullet list of completed work
- **What's in progress / pending:** Any tasks started but not finished, with current state
- **Pick up here next session:** The single most important next action, phrased as a ready-to-paste prompt
- **Open PRs / branches:** Any unmerged branches or PRs created during this session
- **Blockers:** Anything that needs human action (merges, settings changes, credentials, etc.)

Trigger this automatically when the user says things like "closing down", "I'm done", "wrapping up", "pick this up tomorrow", "ending the session", or similar.
