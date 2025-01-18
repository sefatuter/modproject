# modproject

ubuntu 22.04

/modproject
```
sudo apt install python3 python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install flask flask-wtf
```


modsecurity installation
```
cd /opt/
sudo apt update && sudo apt upgrade -y
sudo apt install -y nano gcc g++ make libpcre3 libpcre3-dev zlib1g zlib1g-dev libxml2 libxml2-dev git curl wget openssl libssl-dev libtool autoconf automake perl libperl-dev nginx bison ca-certificates flex gawk pkg-config libxslt1-dev libgd-dev libcurl4-openssl-dev expat libexpat1-dev libmaxminddb-dev libgeoip-dev

git clone --depth 1 -b v3.0.9 https://github.com/SpiderLabs/ModSecurity
git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git
git clone https://github.com/coreruleset/coreruleset.git modsecurity-crs
git clone https://github.com/leev/ngx_http_geoip2_module.git /usr/local/src/ngx_http_geoip2_module
wget http://nginx.org/download/nginx-1.18.0.tar.gz

cd ModSecurity/
git submodule init
git submodule update
./build.sh
./configure
make
make install

cd /opt/
nginx -v
tar -xzvf nginx-1.18.0.tar.gz


./configure --add-dynamic-module=../ModSecurity-nginx --add-dynamic-module=/usr/local/src/ngx_http_geoip2_module --prefix=/usr/share/nginx --sbin-path=/usr/sbin/nginx --with-cc-opt='-g -O2 -ffile-prefix-map=/build/nginx-dSlJVq/nginx-1.18.0=. -flto=auto -ffat-lto-objects -flto=auto -ffat-lto-objects -fstack-protector-strong -Wformat -Werror=format-security -fPIC -Wdate-time -D_FORTIFY_SOURCE=2' --with-ld-opt='-Wl,-Bsymbolic-functions -flto=auto -ffat-lto-objects -flto=auto -Wl,-z,relro -Wl,-z,now -fPIC' --prefix=/usr/share/nginx --conf-path=/etc/nginx/nginx.conf --http-log-path=/var/log/nginx/access.log --error-log-path=/var/log/nginx/error.log --lock-path=/var/lock/nginx.lock --pid-path=/run/nginx.pid --modules-path=/usr/lib/nginx/modules --http-client-body-temp-path=/var/lib/nginx/body --http-fastcgi-temp-path=/var/lib/nginx/fastcgi --http-proxy-temp-path=/var/lib/nginx/proxy --http-scgi-temp-path=/var/lib/nginx/scgi --http-uwsgi-temp-path=/var/lib/nginx/uwsgi --with-compat --with-debug --with-pcre-jit --with-http_ssl_module --with-http_stub_status_module --with-http_realip_module --with-http_auth_request_module --with-http_v2_module --with-http_dav_module --with-http_slice_module --with-threads --with-http_addition_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_sub_module

make modules

mkdir /etc/nginx/modules
cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules/
```

nginx configuration
```
cp /opt/modproject/confs/nginx.conf /etc/nginx/
cd /opt/modsecurity-crs/

mv crs-setup.conf.example crs-setup.conf
mv rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example rules/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
cd /opt/
mv modsecurity-crs/ /usr/local/
mkdir -p /etc/nginx/modsec
cp /opt/ModSecurity/unicode.mapping /etc/nginx/modsec/
cd ModSecurity
mv modsecurity.conf-recommended modsecurity.conf
cp modsecurity.conf /etc/nginx/modsec/

## Configure nano /etc/nginx/modsec/modsecurity.conf after: (SecResponseBodyAccess On)
cp /opt/modproject/confs/modsecurity.conf /etc/nginx/modsec

cd /etc/nginx/modsec/

## Configure nano main.conf after:
cp /opt/modproject/confs/main.conf /etc/nginx/modsec

sudo mkdir -p /root/certs/appcerts.com
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /root/certs/appcerts.com/myapp.key -out /root/certs/appcerts.com/myapp.crt

cp /opt/modproject/confs/appcerts.com.conf /etc/nginx/conf.d
chmod 400 /root/certs/appcerts.com/myapp.key
sudo chmod 644 /var/log/modsec_audit.log
```

