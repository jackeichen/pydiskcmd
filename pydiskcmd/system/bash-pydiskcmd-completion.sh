# bash tab completion for the nvme command line utility

_pysata_cmds="check-PowerMode accessible-MaxAddress identify self-test \
          smart standby read write flush trim version help"

_pynvme_cmds="smart-log id-ctrl id-ns error-log fw-log fw-download fw-commit \
          version help"

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
		"check-PowerMode")
		opts+=" --show_status -h --help"
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
		opts="/dev/sd* "
	fi

	opts+=" "

    case "$1" in
		"check-PowerMode")
		opts+=" -o --output-format -h --help"
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
