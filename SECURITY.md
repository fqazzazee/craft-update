# Security policy — craft-update

## Supported versions

Only the current `main` branch gets security fixes.

## Reporting a vulnerability

Do not open a public issue.

Use [private vulnerability reporting](https://github.com/fqazzazee/craft-update/security/advisories/new),
or email fadi.qazzazee@gmail.com with the details and, if you have one, a proof of
concept.

Expect an acknowledgment within 72 hours and an assessment within a week. If a fix is
warranted, you will get the timeline and credit in the release notes unless you would
rather not be named.

## Scope

**In scope:** the scripts and systemd units in this repository and their default
configuration. Because this tool fetches, builds and installs software on a schedule,
the most serious reports are ones that make it build or install something other than the
intended upstream source, or let an unprivileged user change what it runs.

**Out of scope:** vulnerabilities in the ArtCraft apps themselves (report those
upstream), and anything that requires an attacker to already have the privileges the
issue would grant.
