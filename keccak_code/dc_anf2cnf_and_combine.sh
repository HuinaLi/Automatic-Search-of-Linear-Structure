#!/bin/bash
set -e

ShowUsage() {
    echo "Usage: "
    echo "bash $0 ROUNDS AS DS alg_BASE CNFfile ASpath DSpath (solutions_count)"
    echo ""
    echo "Example: (2 rounds, solve from the beginning)"
    echo "bash $0 2 640 448 /home/n2107349e/SAT/preimage/Optimal_LS keccak224 /home/n2107349e/SAT/preimage/Optimal_LS/modify_AS_geq_640.cnf /home/n2107349e/SAT/preimage/Optimal_LS/modify_640DS_leq_448.cnf"
    echo ""
    echo "Example: (2 rounds, 9 solutions found, we want to solve from the 10th solution)"
    echo "bash $0 2 640 448 /home/n2107349e/SAT/preimage/Optimal_LS keccak224 /home/n2107349e/SAT/preimage/Optimal_LS/modify_AS_geq_640.cnf /home/n2107349e/SAT/preimage/Optimal_LS/modify_640DS_leq_448.cnf 10"
}

if [ "$8" = "" ] || [ "$1" = "--help" ] || [ "$1" = "help" ]; then
    ShowUsage $0
    exit 1
fi

ROUNDS=$1
DG=$2
AS=$3
DS=$4
alg_BASE=$5
file=$6
AS_path=$7
DS_path=$8
solutions_count=$9

BASE=`cd $(dirname "$0");pwd`
echo "bash $0 ${ROUNDS} ${AS} ${DS} ${alg_BASE} ${file} ${solutions_count}"
cd ${BASE}

# combine cnf
combine() {
    echo "start modifying and combining cnf"
    cd ${BASE}
    python combine_object_cnf.py -f1 ${alg_BASE}/${file}.cnf -f2 ${AS_path} -f3 ${DS_path} -o ${alg_BASE}/${file}_AS${AS}_DS${DS}.cnf -r ${ROUNDS}
    echo "output cnf file: ${alg_BASE}/${file}_AS${AS}_DS${DS}.cnf"
}

# solve
solve() {
    echo "start solving $1"
    echo "output solution file: ${alg_BASE}/${file}_AS${AS}_DS${DS}_solution$1.txt"
    set +e
    #nohup cryptominisat5 -t 5 ${alg_BASE}/${file}_AS${AS}_DS${DS}.cnf </dev/null >${alg_BASE}/${file}_AS${AS}_DS${DS}_solution$1.txt 2>&1
    nohup cryptominisat5 -t 20 ${alg_BASE}/${file}_AS${AS}_QS${DS}.cnf </dev/null >${alg_BASE}/${file}_AS${AS}_QS${DS}_solution$1.txt 2>&1
    #nohup /home/n2107349e/cadical/build/cadical ${alg_BASE}/${file}_AS${AS}_DS${DS}.cnf </dev/null >${alg_BASE}/${file}_AS${AS}_DS${DS}_solution$1.txt 2>&1
    set -e
}

# add ban to cnf
ban() {
    echo "start adding ban $1"
    python read_and_ban_solution.py -c ${alg_BASE}/${file}_AS${AS}_DS${DS}.cnf -s ${alg_BASE}/${file}_AS${AS}_DS${DS}_solution$1.txt -r ${ROUNDS} -d ${DG}
    rm -rf ${alg_BASE}/${file}_AS${AS}_DS${DS}_solution$1.txt
}

# iterated solve
iterated_solve() {
    cd ${BASE}
    i=$1
    while true
    do
        solve $i
        CUR_TIME=`date +%Y/%m/%d/%H:%M:%S`
        echo "current time is: ${CUR_TIME}"
        ban $i
        i=$(expr ${i} + 1)
    done
}

main() {
    START_TIME=`date +%Y/%m/%d/%H:%M:%S`
    echo "start time is: ${START_TIME}"

    if [ "${solutions_count}" = "" ]
    then 
        combine 
        solutions_count=1
    fi

    START_TIME=`date +%Y/%m/%d/%H:%M:%S`
    ST=`date +%s.%N`
    echo "solve start time is: ${START_TIME}"

    iterated_solve ${solutions_count}

    ED=`date +%s.%N`
    END_TIME=`date +%Y/%m/%d/%H:%M:%S`
    EXECUTING_TIME=$(printf "%.6f" `echo "${ED} - ${ST}" | bc`)
    echo "total time is: ${EXECUTING_TIME}"
}

main $@