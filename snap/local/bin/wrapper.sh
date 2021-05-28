#!/bin/sh

readonly applications="$(snapctl get applications)"
readonly provider="$(snapctl get provider)"
readonly debug="$(snapctl get debug)"

if [ ! -z "$debug" ]; then
    readonly debug_flag="--debug"
else
    readonly debug_flag=""
fi

if [ ! -z "$applications" ] && [ ! -z "$provider" ]; then
    snapctl set-health okay
    $SNAP/bin/python3 $SNAP/bin/joule --applications "$applications" --provider "$provider" $debug_flag
else
    snapctl set-health blocked "Must set \`applications\` and \`provider\`."
fi
