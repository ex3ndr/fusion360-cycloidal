set -e
rm -fr "$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Cycloidal"
mkdir -p "$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Cycloidal"
cp -r ./sources/* "$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/Cycloidal/"