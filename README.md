# virtual-joypad-tcp

## Server

Set up the server where the virtual joypads are needed

### Install dependencies

Install [vJoy](http://vjoystick.sourceforge.net/site/index.php/download-a-install/download)

```
git clone https://github.com/tidzo/pyvjoy
mv pyvjoy ...\PythonXX\site-packages\
cp "C:\Program Files\vJoy\x86\vJoyInterface.dll" ...\PythonXX\site-packages\pyvjoy\
```

### Run

Run `server.py [ip:port]`


## Client

Run `client.py /dev/input/eventN server.ip:port`
