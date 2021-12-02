set -a
. ./settings.ini
set +a

echo "Stopping application..."
sudo systemctl stop geoconstat

if [ -d venv ]
then
  echo "Suppression du virtual env existant..."
  sudo rm -rf venv
fi

python3 -m venv venv

source venv/bin/activate 
pip install wheel
pip install -r requirements.txt

echo "Creating configuration files if they dont already exist"
if [ ! -f ./config.py ]; then
  envsubst < config.py.sample > ./config.py|| exit 1
fi

echo "Launching application..."
export BASE_DIR=$(readlink -e "${0%/*}")
echo "BASE DIR"
echo $BASE_DIR
envsubst '${USER} ${BASE_DIR} ${gun_num_workers} ${gun_port}' < geoconstat.service | sudo tee /etc/systemd/system/geoconstat.service || exit 1
sudo systemctl daemon-reload || exit 1
sudo systemctl enable geoconstat || exit 1
sudo systemctl start geoconstat || exit 1

