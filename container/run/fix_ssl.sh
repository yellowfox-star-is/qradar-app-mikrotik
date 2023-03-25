echo -n | openssl s_client -connect $QRADAR_CONSOLE_IP:443 -servername $QRADAR_CONSOLE_FQDN | openssl x509 > /opt/app-root/store/certificate_fix.pem
