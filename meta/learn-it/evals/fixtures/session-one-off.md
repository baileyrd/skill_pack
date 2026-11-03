# Session log, 2026-11-02

User: the deploy script fails with "config not found"
Claude: deploy.sh reads `conf/prod.yaml`; the file is `config/prod.yaml`. Fixed the path on line 12. Deploy succeeded.
User: great thanks
