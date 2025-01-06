#vorab installation von git und clone des repositories hier
#sudo apt-get install git
git config --global user.name "drone-I-1"
git config --global user.email "drone-I-1@andrenavaga-park.de"
git config --global credential.helper store
git pull
#in crontab -e
#"@reboot sleep 60 && ~/raspbee_image/startup.sh" >> /var/spool/cron/crontabs/drone-1-2

#"*/15 * * * * ~/raspbee_image/startup.sh" >> /var/spool/cron/crontabs/drone-1-2

#pip install weatherhat
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
#git clone https://github.com/pimoroni/weatherhat-python
#cd weatherhat-python
#sudo ./install.sh

sudo apt install ffmpeg
pip install picamera2
pip install numpy
pip install opencv-python
pip install paho.mqtt
pip install pyyaml
pip install pysmb
pip install astral
pip install psutil
pip install scikit-learn
