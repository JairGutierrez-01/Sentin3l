# Tech Stack

Here is the logic behind the tools I’ve chosen for my guy

## Core engine

I chose Python as the backbone of Sentin3l because it has an incredible ecosystem for parsing URLs and analyzing text without reinventing the wheel.

- **FastAPI:** I’m using this for the backend because it’s fast, modern, and forces me to use Python type hints which makes the code much more reliable. AND, it generates its own documentation (OpenAPI), which truly saves me.

- **Poetry:** To keep my development environment clean. It handles dependencies way better than a simple requirements.txt, ensuring that if you run this project, it works exactly like it does on my machine so i dont have the excuse "hey! it works in muy computer..."

## Data & Privacy: SQLite

Since Sentin3l is about education and privacy, I didn't want a heavy Data base, that's why i´ve chosen SQLite

- It's serverless and local, so your data doesn't travel to a third party cloud.
- It only stores the bare minimum: hashed URLs and detection stats. **No passwords, no names, no fluff.**

## Testing and Quality 

I’ve integrated a few "guardian angels" into my workflow:

- **Bandit:** This is my static analysis buddy. Every time I write code, Bandit checks it for common security holes (like unsafe functions or weak crypto).

- **The Lab (VMware + Kali + Proxmox server):** I don’t test suspicious patterns on my main machine. I use an isolated VMware environment with Kali Linux to simulate attacks and generate phishing samples safely.

## Why this set up?

My philosophy for this stack is simple: Keep it lightweight and transparent. By using these tools, I can focus on what really matters, improving the detection logic while keeping the project portable and easy for anyone.