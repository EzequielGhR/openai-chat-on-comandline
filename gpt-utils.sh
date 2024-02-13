#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )


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

function gpt2() {
    initialize

    python main.py --start-message "${1}" \
        --purpose "${2}" \
        --load-latest "" \
        --load-from-file "" && rollback || handle-error
    
    return
}

function gpt-latest2() {
    initialize

    python main.py --start-message "${1}" \
        --purpose "" \
        --load-latest "True" \
        --load-from-file "" && rollback || handle-error
    
    return
}

function gpt-from-file() {
    initialize

    python main.py --start-message "${2}" \
        --purpose "" \
        --load-latest "" \
        --load-from-file "${1}" && rollback || handle-error
    
    return 
}