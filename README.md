End Game:

A full-stack FastAPI application built with Server-Side Rendering (Jinja2) and Peewee ORM for tracking security coins and apprenticeship duties. Designed and hardened against pen-testing specifications.

Runnign this app: 

pip install -r requirements.txt
python -m fastapi dev main.py
local access: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Running tests: 
pytest --cov=.

Live site:
Production URL: https://api-assignment-swart.vercel.app/

Security:
Token Protection: JWT authentication tokens stored in HttpOnly, SameSite=Lax, and Secure cookies.

Least Privilege: role based protection (Unauthenticated, Authorised, Admin).

Rate Limiting: Rate limiter configured using Fast API/

Data Obfuscation: Internal database UUIDs hidden from client-side UI template. Error handling uses generic authentication failure messages.

Audit Logging: System middleware logs the last 100 HTTP requests, accessible exclusively to admins via /admin/logs.