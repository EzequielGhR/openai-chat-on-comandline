#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

#### THIS SCRIPT SHOULD BE SOURCED ####
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    echo "this script should be sourced"
    exit 1
fi

function initialize() {
    #initialize
    current=`pwd`
    cd "${parent_path}"
    source .venv/bin/activate

    #error handling and rollback
    function rollback() {
        cd "${current}"
        deactivate
    }
    function handle-error() {
        echo "There was an error with the execution"
        rollback
        return 1
    }
}

function gpt() {
    if [ "${1}" == "help" ]; then
        echo "Use gpt [start-message] [chat-purpose] to start a conversation with gpt"
        echo "Example: gpt \"How do I make bread?\" \"cooking\""
        return
    fi

    initialize

    python main.py --start-message "${1}" \
        --purpose "${2}" \
        --load-latest "" \
        --load-from-file "" && rollback || handle-error
    
    return
}

function gpt-latest() {
    if [ "${1}" == "help" ]; then
        echo "Use gpt-latest [start-message] to load latest conversation with gpt using a new message"
        echo "Example: gpt-latest \"How much oven time does it need?\""
        return
    fi

    initialize

    python main.py --start-message "${1}" \
        --purpose "" \
        --load-latest "True" \
        --load-from-file "" && rollback || handle-error
    
    return
}

function gpt-from-file() {
    if [ "${1}" == "help" ]; then
        echo "Use gpt-from-file [file-name] [start-message] to load a conversation by filename with gpt"
        echo "Example: gpt-from-file \"20240213T013639940428.json\" \"What if I don't have yeast?\""
        return
    elif [ -z "${1}" ]; then
        echo "filename missing, please provide a valid json"
        return 1
    fi

    initialize

    python main.py --start-message "${2}" \
        --purpose "" \
        --load-latest "" \
        --load-from-file "${1}" && rollback || handle-error
    
    return 
}