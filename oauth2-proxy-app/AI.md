# Context Memory Preservation Rules
- You are running on a local llama.cpp server with an active 204,800 token sequence map.
- CRITICAL: Never modify or alter the top-level System Prompt text midway through a chat session.
- Keep the system instructions, developer persona, and structural formatting variables completely static.
- All dynamic data updates (such as edited codebase files, console errors, or directory trees) MUST be appended to the bottom inside the active user prompt turn.
