# DTP VLAN Hopping Tool — Matricula: 2023-0316 | ITLA

## Objetivo del Laboratorio
Demostrar **VLAN Hopping** mediante DTP Spoofing (forzar trunk en Gig0/1 del SW-L2) y doble encapsulacion 802.1Q para saltar a VLAN 30.

---

## Topologia (comun a los 3 ataques)

```
Internet (8.8.8.8)
      |
Router  Fa0/0: 20.23.3.1 (GW)
        Fa0/1 -> SW-L2
      |
SW-L2   Gig0/0: router
        Gig0/1: Kali Linux  20.23.3.16  [ATACANTE - dynamic auto VULNERABLE]
        Gig0/2: PC-Victima  20.23.3.50  [VLAN 20]
        Gig0/3: PC-Admin    20.23.3.65  [VLAN 30 - objetivo del hopping]
```

### Tabla de interfaces

| Dispositivo | Puerto | Modo | Conectado a | IP |
|---|---|---|---|---|
| Router | Fa0/0 | — | Internet | 20.23.3.1 |
| Router | Fa0/1 | — | SW-L2 Gig0/0 | — |
| SW-L2 | Gig0/0 | access | Router Fa0/1 | — |
| SW-L2 | Gig0/1 | **dynamic auto** | Kali eth0 | — |
| SW-L2 | Gig0/2 | access VLAN 20 | PC-Victima | — |
| SW-L2 | Gig0/3 | access VLAN 30 | PC-Admin | — |
| Kali | eth0 | — | SW-L2 Gig0/1 | 20.23.3.16 |
| PC-Victima | eth0 | — | SW-L2 Gig0/2 | 20.23.3.50 |
| PC-Admin | eth0 | — | SW-L2 Gig0/3 | 20.23.3.65 |

> Gig0/1 en dynamic auto es el puerto vulnerable para negociacion DTP.

---

## Objetivo del Script

`dtp_vlan_hopping.py` construye tramas DTP con TLVs en modo Desirable, forzando trunk en Gig0/1. Con trunk activo usa doble encapsulacion 802.1Q para saltar a VLAN 30.

**Ruta DTP:**
```
Kali eth0 -> SW-L2 Gig0/1 (dynamic auto)
  Puerto negocia TRUNK -> Kali recibe trafico de todas las VLANs
```

**Ruta Hopping:**
```
Kali eth0 -> [VLAN1][VLAN30] -> SW-L2 Gig0/1
  SW-L2 despoja etiqueta VLAN1 (nativa)
  -> reenvía [VLAN30] hacia Gig0/3
  -> PC-Admin 20.23.3.65 recibe el frame
```

---

## Requisitos

```bash
Linux (Kali Linux)
Python 3.8+
pip install scapy
sudo / root
Kali conectada a SW-L2 Gig0/1 (dynamic auto)
```

---

## Parametros

| Parametro | Default | Descripcion |
|---|---|---|
| -i | eth0 | Interfaz (SW-L2 Gig0/1) |
| -m | requerido | dtp, hopping, ambos |
| --vlan-nativa | 1 | VLAN nativa outer tag |
| --vlan-objetivo | 30 | VLAN objetivo PC-Admin |
| --ip-destino | 20.23.3.65 | IP PC-Admin |
| -p | False | Re-envio periodico trunk |

---

## Uso

```bash
# Solo DTP (convertir Gig0/1 en trunk)
sudo python3 dtp_vlan_hopping.py -m dtp

# DTP + mantener trunk activo
sudo python3 dtp_vlan_hopping.py -m dtp -p

# Solo hopping doble encapsulacion
sudo python3 dtp_vlan_hopping.py -m hopping \
  --vlan-nativa 1 --vlan-objetivo 30 --ip-destino 20.23.3.65

# Ataque completo
sudo python3 dtp_vlan_hopping.py -m ambos \
  --vlan-nativa 1 --vlan-objetivo 30 --ip-destino 20.23.3.65 -p
```

---

## Configuracion Cisco

### Router
```
hostname ROUTER
interface FastEthernet0/0
 ip address 20.23.3.1 255.255.255.240
 no shutdown
interface FastEthernet0/1
 no ip address
 no shutdown
```

### SW-L2 (puerto Gig0/1 vulnerable)
```
hostname SW-L2
interface GigabitEthernet0/0
 switchport mode access
 no shutdown
interface GigabitEthernet0/1
 switchport mode dynamic auto
 no shutdown
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 20
 no shutdown
interface GigabitEthernet0/3
 switchport mode access
 switchport access vlan 30
 no shutdown
vlan 20
 name Usuarios
vlan 30
 name Admin
```

---

## Contramediadas

| Medida | Comando | Contra |
|---|---|---|
| Deshabilitar DTP | switchport nonegotiate | DTP |
| Modo access fijo | switchport mode access | DTP |
| Cambiar VLAN nativa | switchport trunk native vlan 999 | Doble encap |
| Limitar VLANs trunk | switchport trunk allowed vlan 20,30 | Ambos |

---
*Laboratorio academico | ITLA | Matricula: 2023-0316*
