#!/bin/bash
IFS=$'\n'

PROMPT=$1
# JSON=$(cat)
# JSON=$(read -t 1)
JSON=$(timeout 1 cat /dev/stdin)
TOOL=$(echo $JSON | jq -r '.tool_name')
COMMAND=$(echo $JSON | jq -r '.tool_input.command')

PROMPT="$PROMPT\n\nUsing tool: $TOOL\nRunning command: $COMMAND\n\nContent:\n\n$JSON"

DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1517018133011894395/eklbj-ntpKkXcbsgW9etVK7bCIhyj5qYEGvXE39YyVNHgVsQmXQFdS2BhcghIENWp07-"

 curl -i -H "Accept: application/json" -H "Content-Type:application/json" -X POST --data "{\"content\": \"$PROMPT\"}" $DISCORD_WEBHOOK_URL