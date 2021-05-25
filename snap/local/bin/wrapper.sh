#!/bin/sh

readonly application="$(snapctl get application)"
readonly provider="$(snapctl get provider)"
readonly debug="$(snapctl get debug)"

if [ ! -z "$debug" ]; then
    readonly debug_flag="--debug"
else
    readonly debug_flag=""
fi

if [ ! -z "$application" ] && [ ! -z "$provider" ]; then
    snapctl set-health okay
    $SNAP/bin/python3 $SNAP/bin/joule --application "$application" --provider "$provider" $debug_flag
else
    snapctl set-health blocked "Must set \`application\` and \`provider\`."
fi
