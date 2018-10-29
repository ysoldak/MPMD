#!/bin/bash

VERSION=${1:-3.5}

# -----------------------------------------------------------------------------

CURA_HOME=${CURA_HOME:-${HOME}"/Library/Application Support/cura"}
CURA_DIR="${CURA_HOME}/${VERSION}"

# -----------------------------------------------------------------------------

pgrep -q cura
if [ "$?" == "0" ]; then
    echo "Cura is running, exit and run this script again"
    exit 1
fi

# -----------------------------------------------------------------------------

echo "Diff machine settings with cura dir"
echo "   ${CURA_DIR}"
echo 

for file in `find -E . -regex ".*\.(cfg|stl|json)" | grep -v cura.cfg | sort`; do
    dirname=`dirname $file | sed s,\./,,`
    basename=`basename $file`
    echo "  ± ${dirname}/${basename}"
    diff "`pwd`/${dirname}/${basename}" "${CURA_DIR}/${dirname}/${basename}" 
    echo
done

echo
echo "Done!"
