# modproject

<img width="1901" height="961" alt="image" src="https://github.com/user-attachments/assets/7eb0ebf6-5598-4a13-a462-5ef76e3c5046" />

<img width="1901" height="960" alt="image" src="https://github.com/user-attachments/assets/2f760a52-369b-4eec-837c-c90f43442e27" />

<img width="1902" height="957" alt="image" src="https://github.com/user-attachments/assets/217e3455-d526-48f9-9c2e-aa98bdbcefca" />

<img width="1920" height="1000" alt="image" src="https://github.com/user-attachments/assets/5c22f195-8931-40bb-a20f-53654fda2906" />


## package insallation

ubuntu 22.04

/modproject
```
sudo apt install python3 python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install flask flask-wtf
```




## modsecurity installation

To install NGINX with ModSecurity on Ubuntu, follow these steps:

---

### **Step 1: Update System Packages**
Ensure your system packages are up-to-date:
```bash
sudo apt update
sudo apt upgrade -y
```

---

### **Step 2: Install NGINX**
Install the NGINX package:
```bash
sudo apt install nginx -y
```

---

### **Step 3: Install Required Dependencies**
Install dependencies required for ModSecurity:
```bash
sudo apt install libnginx-mod-http-modsecurity -y
```

This package provides the ModSecurity module for NGINX.

---

### **Step 4: Enable ModSecurity in NGINX**
1. Open the main NGINX configuration file:
   ```bash
   sudo nano /etc/nginx/nginx.conf
   ```

2. Add the following line in the `http` block to enable the ModSecurity module:
   ```nginx
   modsecurity on;
   modsecurity_rules_file /etc/nginx/modsecurity_includes.conf;
   ```

   - `modsecurity on;`: Enables ModSecurity.
   - `modsecurity_rules_file`: Specifies the main ModSecurity configuration file.

3. Save and exit the editor.

---

### **Step 5: Configure ModSecurity**

The OWASP CRS provides predefined security rules for ModSecurity.
1. Edit the configuration file uncomment  the following:

   ```bash

   Change:
   ```text 
     #include /usr/share/modsecurity-crs/owasp-crs.load
   ```
   To:
  ```text
     include /usr/share/modsecurity-crs/owasp-crs.load
  ```


3. Enable ModSecurity, by editing /etc/nginx/modsecurity.conf via attaching it to every transaction.
   
   Change:
   ```text
   SecRuleEngine DetectionOnly
   ```
   To:
   ```text
   SecRuleEngine On
   ```

   - `DetectionOnly`: Logs potential threats but does not block them.
   - `On`: Actively blocks threats.

4. Check /usr/share/modsecurity-crs/owasp-crs.load file. All should be uncommented. Comment IncludeOptional lines

  Change:
  ```text
    Include /etc/modsecurity/crs/crs-setup.conf
    IncludeOptional /etc/modsecurity/crs/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
    Include /usr/share/modsecurity-crs/rules/*.conf
    IncludeOptional /etc/modsecurity/crs/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf
  ```

  To:
  ```text
    Include /etc/modsecurity/crs/crs-setup.conf
    #IncludeOptional /etc/modsecurity/crs/REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf
    Include /usr/share/modsecurity-crs/rules/*.conf
    # IncludeOptional /etc/modsecurity/crs/RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf
  ```


### **Step 7: Test and Restart NGINX**
1. Test the NGINX configuration:
   ```bash
   sudo nginx -t
   ```

2. If the test is successful, restart NGINX:
   ```bash
   sudo systemctl restart nginx
   ```



### **Step 8: Verify ModSecurity**
To confirm ModSecurity is active:
1. Check NGINX logs for ModSecurity activity:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   sudo tail -f /var/log/nginx/modsec_audit.log
   ```

2. Trigger a security event by accessing the server with a suspicious query, such as:
   ```bash
   curl "http://your-server-ip/?test=<script>alert('xss')</script>"
   ```

If ModSecurity is active, you should see logs related to this request.

---

### Optional: Fine-Tune ModSecurity Rules
- You can customize or disable specific rules by editing files in `/etc/nginx/modsec/crs/rules/`.
- Use `SecRuleRemoveById` to disable specific rules.

Now you have successfully installed and configured NGINX with ModSecurity on Ubuntu!


## manual installation 
```
cd /opt/
sudo apt update && sudo apt upgrade -y
sudo apt install -y nano gcc g++ make sqlite3 libpcre3 libpcre3-dev zlib1g zlib1g-dev libxml2 libxml2-dev git curl wget openssl libssl-dev libtool autoconf automake perl libperl-dev nginx bison ca-certificates flex gawk pkg-config libxslt1-dev libgd-dev libcurl4-openssl-dev expat libexpat1-dev libmaxminddb-dev libgeoip-dev

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


```
sudo chown -R www-user:www-user /usr/local/modsecurity-crs/rules/
```
