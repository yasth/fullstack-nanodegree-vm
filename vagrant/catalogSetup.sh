
apt-get -qqy update
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
pip install -r /vagrant/catalog/requirements.txt
cd /vagrant/catalog
python ./models.py
