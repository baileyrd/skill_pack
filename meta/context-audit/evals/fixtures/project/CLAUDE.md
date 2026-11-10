# Project rules

- Write clean, readable code.
- Always handle errors properly.
- Use tabs for indentation.
- Be natural and use a good tone in comments.
- Never use the word "utilize" in docstrings (it came up once in review).
- Run tests with `pytest -q` before committing.
- Prefer small functions.
- Write clean code that is easy to read.
- Deploy with `make deploy` from main only.
- API handlers return JSON envelopes `{data, error}`.
