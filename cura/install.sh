#!/bin/bash

VERSION=${1:-3.5}
TYPE=${2:-definition_changes}

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

echo "Installing machine into cura dir"
echo "  ${CURA_DIR}"
echo

for file in `find -E . -regex ".*\.(cfg|stl|json|fdm_material)" | grep -v cura.cfg`; do
    dirname=`dirname $file | sed s,\./,,`
    basename=`basename $file`
    mkdir -p "${CURA_DIR}/${dirname}"
    if [ "${TYPE}" == "all" ] || [ "${TYPE}" == "${dirname}" ]; then
        # force install start/end gcode definitions
        echo "  > ${basename}"
        cp "`pwd`/${dirname}/${basename}" "${CURA_DIR}/${dirname}/${basename}"
    else
        # do not overwrite file at destination to preserve user settings, quality selected, etc
        echo "  ? ${basename}"
        cp -n "`pwd`/${dirname}/${basename}" "${CURA_DIR}/${dirname}/${basename}"
    fi
    # Linking does not work since Cura re-creates configuration files instead of updating them
    #ln -s `pwd`/${dirname}/${basename} "${CURA_DIR}/${dirname}/${basename}"
done

echo "  ? cura.cfg"
cp -n "`pwd`/cura.cfg" "${CURA_DIR}/cura.cfg"

echo
echo "Done!"
