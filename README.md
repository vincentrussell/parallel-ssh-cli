# parallel-ssh-cli

cli wrapper arround parallel-ssh.  See: https://parallel-ssh.readthedocs.io/en/latest/

## installing prerequisites

```console
yum install -y https://repo.ius.io/ius-release-el7.rpm
yum -y update
yum install -y wget systemd openssl-devel sudo vim python36u python36u-libs python36u-devel python36u-pip
yum groupinstall -y "Development Tools"
cd /bin
cd $OLDPWD
wget https://cmake.org/files/v3.6/cmake-3.6.2.tar.gz
tar -zxvf cmake-3.6.2.tar.gz
cd cmake-3.6.2
./bootstrap --prefix=/usr/local
make
make install
pip3 install wheel
pip3 install pyinstaller
pip3 install termcolor
CFLAGS="-fpermissive -std=c++11" pip3 install parallel-ssh

```

## installing executable

```console
sudo python3 setup.py install
```


