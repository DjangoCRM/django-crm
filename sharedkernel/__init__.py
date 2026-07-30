"""Shared kernel package for cross-app primitives.

The sharedkernel app may import only Django and the standard library.
Every other project app may import sharedkernel, but sharedkernel must
never import common, crm, tasks, massmail, analytics, chat, quality,
help, settings, or voip.
"""
