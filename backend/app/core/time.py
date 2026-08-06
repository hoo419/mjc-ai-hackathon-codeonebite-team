from datetime import timedelta, timezone

# The whole project reports timestamps in KST (API_CONTRACT.md date/time
# rule), so this is the one place that value lives.
KST = timezone(timedelta(hours=9))
