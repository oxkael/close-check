# Deployment — Running the scheduler as a background service

This document shows example service entries for running the CloseWatch scheduler
in production on Linux (systemd) and on Windows (Scheduled Task / `schtasks`).

## Systemd example
- File: `scripts/systemd/closewatch.service`
- Copy the file to `/etc/systemd/system/closewatch.service`, update paths, then enable:

```bash
sudo cp scripts/systemd/closewatch.service /etc/systemd/system/closewatch.service
sudo systemctl daemon-reload
sudo systemctl enable --now closewatch.service
sudo journalctl -u closewatch -f
```

Notes:
- Update `WorkingDirectory` to the project root and `ExecStart` to point to your virtualenv Python. Example:

```
WorkingDirectory=/home/you/Closecheck
ExecStart=/home/you/Closecheck/.venv/bin/python -m closewatch.cli scheduler
```

- The service runs the scheduler which will perform hourly ingestion and a daily recalibration at 03:00 UTC (APScheduler) or the fallback loop if APScheduler is not installed.

## Windows Scheduled Task (example using `schtasks`)

Run from an elevated PowerShell prompt to create a scheduled task that starts at boot and restarts on failure. Adjust paths for your environment.

```powershell
$action = 'C:\Users\user\Desktop\Closecheck\\.venv\\Scripts\\python.exe -m closewatch.cli scheduler'
schtasks /Create /SC ONSTART /TN "CloseWatch Scheduler" /TR $action /RL HIGHEST /F

# To run now
schtasks /Run /TN "CloseWatch Scheduler"
```

Alternatively you can use Task Scheduler GUI to create a task that runs the same `python -m closewatch.cli scheduler` command under a specific user account, starts at system boot, and restarts on failure.

## Operational tips
- Ensure the service runs with a working directory of the project root so relative paths (logs, DB) resolve correctly.
- Prefer running under a dedicated non-root user with access to the venv and project files.
- Monitor logs via `journalctl -u closewatch` on systemd, or configure the scheduled task to write stdout/stderr to a file on Windows.
