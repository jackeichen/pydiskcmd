# SPDX-FileCopyrightText: 2022 The pydiskcmd Authors
#
# SPDX-License-Identifier: LGPL-2.1-or-later
# bash tab completion for the nvme command line utility

def get_completion():
    text="""# This is a bash completion for pydiskcmd
_pysata_cmds="list check-PowerMode accessible-MaxAddress identify sanitize self-test set-feature \
          read-log smart-read-log smart smart-return-status standby read write flush trim \
          download-fw trusted-receive read-verify-sector write-log write-uncorrectable \
          version help"

_pynvme_cmds="list list-subsys smart-log id-ctrl id-ns error-log fw-log fw-download fw-commit \
          format sanitize persistent-event-log device-self-test self-test-log telemetry-log \
          sanitize-log get-feature set-feature list-ctrl list-ns nvme-create-ns nvme-delete-ns \
          nvme-attach-ns nvme-detach-ns commands-se-log pcie flush read write get-lba-status \
          compare dsm write-uncor write-zeroes get-log reset subsystem-reset show-regs version help"

_pyscsi_cmds="list inq getlbastatus readcap luns mode-sense log-sense read write \
          smart-simulate sync cdb-passthru se-protocol-in version help"


pysata_list_opts () {
    local opts=""
    local compargs=""

    local nonopt_args=0
    for (( i=0; i < ${#words[@]}-1; i++ )); do
        if [[ ${words[i]} != -* ]]; then
            let nonopt_args+=1
        fi
    done

    if [ $nonopt_args -eq 2 ]; then
        opts="/dev/sd* "
    fi

    opts+=" "

    case "$1" in
        "list")
        opts+=" -o --output-format= -h --help"
        ;;
        "check-PowerMode")
        opts+=" --show_status -h --help"
        ;;
        "accessible-MaxAddress")
        opts+=" --show_status -h --help"
        ;;
        "identify")
        opts+=" -o --output-format= --show_status -h --help"
        ;;
        "sanitize")
        opts+=" -f --feature= --clear-failed --zoned-no-reset --invert --definitive \
            -n --owpass= -p --ovrpat= --force -h --help"
        ;;
        "self-test")
        opts+=" -t --test= --show_status -h --help"
        ;;
        "set-feature")
        opts+=" -f --feature= -c --count= -l --lba= --show_status --guideline \
            -h --help"
        ;;
        "trusted-receive")
        opts+=" -p --protocol= -s --sp= -i --INC_512= -l --alloclen= \
            -o --output-format= -h --help"
        ;;
        "smart")
        opts+=" --show_status -h --help"
        ;;
        "smart-return-status")
        opts+=" --show_status -h --help"
        ;;
        "read-log")
        opts+=" -l --log-address= -p --page-number= -c --count= -f --feature= \
            -o --output-format= --show_status -h --help"
        ;;
        "write-log")
        opts+=" -l --log-address= -p --page-number= -c --count= -d --data= \
            -f --data-file= -b --block-size= --show_status -h --help"
        ;;
        "smart-read-log")
        opts+=" -l --log-address= -c --count= -o --output-format= \
            --show_status -h --help"
        ;;
        "standby")
        opts+=" --show_status -h --help"
        ;;
        "read")
        opts+=" -s --start-block= -c --block-count= -b --block-size= \
            --show_status -h --help"
        ;;
        "read-verify-sector")
        opts+=" -s --start-block= -c --block-count= -b --block-size= \
            --show_status -h --help"
        ;;
        "write")
        opts+=" -s --start-block= -c --block-count= -d --data= \
            -f --data-file= -b --block-size= --show_status -h --help"
        ;;
        "write-uncorrectable")
        opts+=" -l --lba= -c --count= -f --feature= \
             -h --help"
        ;;
        "flush")
        opts+=" --show_status -h --help"
        ;;
        "trim")
        opts+=" -r --block_range= --show_status -h --help"
        ;;
        "download-fw")
        opts+=" -f --file= -c --code= -x --xfer= -h --help"
        ;;
        "version")
        opts+=""
            ;;
        "help")
        opts+=""
            ;;
    esac

        opts+=" -h --help"

    COMPREPLY+=( $( compgen $compargs -W "$opts" -- $cur ) )

    return 0
}


pyscsi_list_opts () {
    local opts=""
    local compargs=""

    local nonopt_args=0
    for (( i=0; i < ${#words[@]}-1; i++ )); do
        if [[ ${words[i]} != -* ]]; then
            let nonopt_args+=1
        fi
    done

    if [ $nonopt_args -eq 2 ]; then
        opts="/dev/sd* "
    fi

    opts+=" "

    case "$1" in
        "list")
        opts+=" -o --output-format= -h --help"
        ;;
        "inq")
        opts+=" -p --page= -o --output-format= -l --alloclen= \
            -h --help"
        ;;
        "cdb-passthru")
        opts+=" -r --raw-cdb= -l ---data-len= -f --data-file= -d --direction= \
            -b --block-size= -o --output-format= -h --help"
        ;;
        "getlbastatus")
        opts+=" -l --lba= -o --output-format= -h --help"
        ;;
        "readcap")
        opts+=" -o --output-format= -h --help"
        ;;
        "luns")
        opts+=" -o --output-format= -h --help"
        ;;
        "se-protocol-in")
        opts+=" -p --protocol= -s --sp= -i --INC_512= -l --alloclen= \
            -o --output-format= -h --help"
        ;;
        "smart-simulate")
        opts+=" -o --output-format= -h --help"
        ;;
        "mode-sense")
        opts+=" -p --page= -s --subpage= -o --output-format= -l --alloclen= \
            -h --help"
        ;;
        "log-sense")
        opts+=" -p --page= -l --alloclen= -s --subpage= -o --output-format= \
            -h --help"
        ;;
        "sync")
        opts+=" -s --start-block= -c --block-count= -i --immed= \
            -g --group-number= -h --help"
        ;;
        "read")
        opts+=" -s --start-block= -c --block-count= -b --block-size= \
            -h --help"
        ;;
        "write")
        opts+=" -s --start-block= -c --block-count= -d --data= \
            -f --data-file= -b --block-size= -h --help"
        ;;
        "version")
        opts+=""
        ;;
        "help")
        opts+=""
        ;;
    esac

        opts+=" -h --help"

    COMPREPLY+=( $( compgen $compargs -W "$opts" -- $cur ) )

    return 0
}


pynvme_list_opts () {
        local opts=""
    local compargs=""

    local nonopt_args=0
    for (( i=0; i < ${#words[@]}-1; i++ )); do
        if [[ ${words[i]} != -* ]]; then
            let nonopt_args+=1
        fi
    done

    if [ $nonopt_args -eq 2 ]; then
        opts="/dev/nvme* "
    fi

    opts+=" "

    case "$1" in
        "list")
        opts+=" -o --output-format= -h --help"
        ;;
        "smart-log")
        opts+=" -o --output-format= -h --help"
        ;;
        "id-ctrl")
        opts+=" -o --output-format= -h --help"
        ;;
        "id-ns")
        opts+=" -n --namespace-id= -o --output-format= -h --help"
        ;;
        "get-log")
        opts+=" -n --namespace-id= -i --log-id= -l --log-len= -o --lpo= \
            -s --lsp= -S --lsi= -r --rae= -U --uuid-index= -y --csi= -O --ot= \
            --output-format= -h --help"
        ;;
        "error-log")
        opts+=" -o --output-format= -h --help"
        ;;
        "commands-se-log")
        opts+=" -o --output-format= -h --help"
        ;;
        "fw-log")
        opts+=" -o --output-format= -h --help"
        ;;
        "sanitize-log")
        opts+=" -o --output-format= -h --help"
        ;;
        "reset")
        opts+=" -h --help"
        ;;
        "subsystem-reset")
        opts+=" -h --help"
        ;;
        "fw-download")
        opts+=" -f --fw= -x --xfer= -o --offset= -h --help"
        ;;
        "fw-commit")
        opts+=" -s --slot= -a --action= -h --help"
        ;;
        "format")
        opts+=" -n --namespace-id= -l --lbaf= -s --ses= -i --pi= \
            -p --pil= -h --help"
        ;;
        "sanitize")
        opts+=" -d --no-dealloc -i --oipbp= -n --owpass= -u --ause= \
            -a --sanact= -p --ovrpat= -h --help"
        ;;
        "persistent-event-log")
        opts+=" -a --action= -o --output-format= -f --filter= \
            -h --help"
        ;;
        "device-self-test")
        opts+=" -n --namespace-id= -s --self-test-code= -h --help"
        ;;
        "self-test-log")
        opts+=" -o --output-format= -h --help"
        ;;
        "telemetry-log")
        opts+=" -o --output-file= -g --host-generate -c --controller-init \
            -d --data-area -h --help"
        ;;
        "get-feature")
        opts+=" -n --namespace-id= -f --feature-id= -s --sel= -l --data-len \
            -c --cdw11= -o --output-format= -h --help"
        ;;
        "set-feature")
        opts+=" -n --namespace-id= -f --feature-id= -v --value= -d --data= \
            -c --cdw12= -s --save -h --help"
        ;;
        "list-ctrl")
        opts+=" -c --cntid= -n --namespace-id= -o --output-format= \
            -h --help"
        ;;
        "list-ns")
        opts+=" -a --all -n --namespace-id= -o --output-format= \
            -h --help"
        ;;
        "nvme-create-ns")
        opts+=" -s --nsze= -c --ncap= -f --flbas= -d --dps= -m --nmic= \
            -a --anagrp-id= -i --nvmset-id -h --help"
        ;;
        "nvme-delete-ns")
        opts+=" -n --namespace-id= -h --help"
        ;;
        "nvme-attach-ns")
        opts+=" -n --namespace-id= -c --controllers= -h --help"
        ;;
        "nvme-detach-ns")
        opts+=" -n --namespace-id= -c --controllers= -h --help"
        ;;
        "pcie")
        opts+=" -p --power= --slot_num= -d --detail= -h --help"
        ;;
        "flush")
        opts+=" -n --namespace-id= -h --help"
        ;;
        "read")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -o --output-format= -h --help"
        ;;
        "write")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -d --data= -f --data-file= -h --help"
        ;;
        "compare")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -f --data-file= -h --help"
        ;;
        "dsm")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -f --data-file= -h --help"
        ;;
        "write-uncor")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -h --help"
        ;;
        "write-zeroes")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -h --help"
        ;;
        "get-lba-status")
        opts+=" -n --namespace-id= -s --start-block= -c --block-count= \
            -e --entry-count= -a --action-type= -o --output-format= \
            -t --timeout= -h --help"
        ;;
        "show-regs")
        opts+=" -o --output-format= -h --help"
        ;;
        "version")
        opts+=""
            ;;
        "help")
        opts+=""
            ;;
    esac

        opts+=" -h --help"

    COMPREPLY+=( $( compgen $compargs -W "$opts" -- $cur ) )

    return 0
}


_pysata_subcmds () {
        local cur prev words cword
    _init_completion || return

    if [[ ${#words[*]} -lt 3 ]]; then
        COMPREPLY+=( $(compgen -W "$_pysata_cmds" -- $cur ) )
    else
        pysata_list_opts ${words[1]} $prev
    fi

    return 0
}

_pyscsi_subcmds () {
        local cur prev words cword
    _init_completion || return

    if [[ ${#words[*]} -lt 3 ]]; then
        COMPREPLY+=( $(compgen -W "$_pyscsi_cmds" -- $cur ) )
    else
        pyscsi_list_opts ${words[1]} $prev
    fi

    return 0
}

_pynvme_subcmds () {
        local cur prev words cword
    _init_completion || return

    if [[ ${#words[*]} -lt 3 ]]; then
        COMPREPLY+=( $(compgen -W "$_pynvme_cmds" -- $cur ) )
    else
        pynvme_list_opts ${words[1]} $prev
    fi

    return 0
}

complete -o default -F _pysata_subcmds pysata

complete -o default -F _pynvme_subcmds pynvme

complete -o default -F _pyscsi_subcmds pyscsi
"""
    return text
