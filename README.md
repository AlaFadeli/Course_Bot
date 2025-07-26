# ENP Course Bot

A Telegram bot designed to help ENP students store, retrieve, and share academic materials efficiently.
Built using Python, PostgreSQL, and `python-telegram-bot`.

---

## Features

- `/upload` --Upload multiple academic materials (admin only)
- `/get` --Retrieve files contained in a module/type
- `/search` --Search files by name or keyword
- `/delete` --Delete files (admin only)
- `/register`--Register using your email (rquired before usage)

---

## How it works?

```mermaid
graph TD
  A[User] -->|Sends Command| B(Bot)
  B --> C{Is Registered?}
  C -->|Yes| D(Query Database)
  C -->|No| E(Send Access Denied Message)
  D --> F(Return Result / Perform Action)
```

---
## Access Control

- Registered users can :
  - get files
  - search files
  - list directories
- Admins can:
  - upload new files
  - delete files
  - check registered list

## Tech Stack

## Demo Preview

### Start:
![Start](/start.gif)

## Contact
- **Bot:**
[@ENPcoursebot](https://t.me/ENPcoursebot)
- **email**:
[course_bot](enpcourse.bot@gmail.com)



