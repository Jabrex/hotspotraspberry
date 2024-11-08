import os
import subprocess

# Hotspot yapılandırma ayarları
SSID = "RaspberryPiHotspot"
PASSWORD = "raspberry123"  # En az 8 karakter olmalı

# `hostapd.conf` dosyasını ayarla
hostapd_config = f"""
interface=wlan0
driver=nl80211
ssid={SSID}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={PASSWORD}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
"""

# `dnsmasq.conf` dosyasını ayarla
dnsmasq_config = """
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
"""

try:
    # hostapd.conf dosyasını yaz
    with open('/etc/hostapd/hostapd.conf', 'w') as f:
        f.write(hostapd_config)

    # hostapd ayar dosyasını belirle
    subprocess.run(["sudo", "sed", "-i", "s|#DAEMON_CONF=\"\"|DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"|", "/etc/default/hostapd"], check=True)

    # dnsmasq.conf dosyasını yedekle ve yeniden yaz
    subprocess.run(["sudo", "mv", "/etc/dnsmasq.conf", "/etc/dnsmasq.conf.orig"], check=True)
    with open('/etc/dnsmasq.conf', 'w') as f:
        f.write(dnsmasq_config)

    # IP adresini wlan0 için statik yap
    subprocess.run(["sudo", "ifconfig", "wlan0", "192.168.4.1"], check=True)

    # `sysctl.conf` dosyasını ayarla
    subprocess.run(["sudo", "sed", "-i", "s/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/", "/etc/sysctl.conf"], check=True)
    subprocess.run(["sudo", "sysctl", "-p"], check=True)

    # iptables ile NAT yapılandırmasını ekle
    subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "wlan0", "-j", "MASQUERADE"], check=True)

    # Ayarları kaydet
    subprocess.run(["sudo", "sh", "-c", "iptables-save > /etc/iptables.ipv4.nat"], check=True)

    # Servisleri yeniden başlat
    subprocess.run(["sudo", "systemctl", "unmask", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "restart", "hostapd"], check=True)
    subprocess.run(["sudo", "systemctl", "restart", "dnsmasq"], check=True)

    print("Hotspot başarıyla ayarlandı ve etkinleştirildi.")

except subprocess.CalledProcessError as e:
    print(f"Bir hata oluştu: {e}")
except Exception as e:
    print(f"Beklenmeyen bir hata oluştu: {e}")
