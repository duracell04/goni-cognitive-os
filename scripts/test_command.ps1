$body = @{ text = "What am I looking at? Explain the current screen." } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/command" -Method Post -ContentType "application/json" -Body $body
