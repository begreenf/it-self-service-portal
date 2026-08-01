# IT Self-Service Portal

## Problem
A huge share of helpdesk tickets are the same handful of issues over and over: forgotten
passwords, VPN problems, printer issues. Every one of those still costs a phone call or an email
and a few minutes of a tech's time, even though the fix is almost always the same three steps.

## Solution
A small, clean web portal with two parts: a searchable knowledge base for the issues people can
usually fix themselves, and a request form that creates a ticket (with a trackable ticket number)
for the ones that need a human. It's a fully working app — not a mockup — built with Flask and
SQLite so it can be run and clicked through end to end.

## Key features
- **Searchable knowledge base** with step-by-step troubleshooting guides (password resets, VPN,
  Wi-Fi, Outlook sync, Teams/SharePoint access, slow laptops, printing).
- **Request form** that creates a real ticket in a local queue and returns a ticket number
  (e.g. `TCK-410689`).
- **Ticket status lookup** so users can check progress without calling IT.
- **Read-only admin queue view** — what a tech would see on their side.
- Clean, responsive UI with no external CSS framework — plain, well-organized CSS.

## Tech stack
Python, Flask, SQLite, Jinja2, HTML/CSS

## Running it
```bash
pip install -r requirements.txt
python app.py
# -> open http://127.0.0.1:5000
```

## Why this matters for clients
This demonstrates full-stack delivery, not just scripting: routing, a real form-to-database flow,
server-rendered templates, and a UI that doesn't look like a bootcamp exercise. For a client, it's
a proof that a "small internal tool" request (a dashboard, a request form, a status page) is
something I can build and ship, not just talk about.

---
*Personal/demo project. Not connected to a real Active Directory or ticketing system — the ticket
queue is a local SQLite database so the whole flow runs standalone. Happy to wire this into a
real helpdesk system (Zendesk, Freshservice, ServiceNow, etc.) or real AD password reset APIs on
a client project.*
