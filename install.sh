sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip python3-tk

python3 -m venv venv
source ./venv/bin/activate
python3 -m pip install -r requirements.txt