# DTP VLAN Hopping — Convertir Access en Trunk
**Diego Marte | Matrícula: 2023-0316 | ITLA — Seguridad de Redes**

## Objetivo del Laboratorio
Demostrar VLAN Hopping mediante dos técnicas: (1) DTP Spoofing, enviando tramas DTP en modo Desirable para forzar al switch a negociar trunk, y (2) Doble Encapsulación 802.1Q, para acceder a VLANs restringidas.

## Topología
```
Internet
    |
Router (Fa0/0: 20.23.3.1)
    |
SW-L2  Gig0/0 -> Router
       Gig0/1 -> Kali Linux 20.23.3.16  [ATACANTE, dynamic auto]
       Gig0/2 -> PC-Victima 20.23.3.50  [VLAN 20]
       Gig0/3 -> PC-Admin   20.23.3.65  [VLAN 30 - objetivo]
```

## Uso
```bash
# Solo DTP (negociar trunk)
sudo python3 dtp_vlan_hopping.py -m dtp

# Doble encapsulación 802.1Q
sudo python3 dtp_vlan_hopping.py -m hopping --vlan-nativa 1 --vlan-objetivo 30 --ip-destino 20.23.3.65

# Ataque completo (DTP + Hopping + persistente)
sudo python3 dtp_vlan_hopping.py -m ambos --vlan-nativa 1 --vlan-objetivo 30 --ip-destino 20.23.3.65 -p
```

## Parámetros
| Parámetro | Default | Descripción |
|---|---|---|
| -i | eth0 | Interfaz de red |
| -m | requerido | dtp \| hopping \| ambos |
| --vlan-nativa | 1 | VLAN nativa del trunk (outer tag) |
| --vlan-objetivo | 30 | VLAN a la que saltar (inner tag) |
| --ip-destino | 20.23.3.65 | IP en la VLAN objetivo |
| -p | False | Modo persistente (re-envía DTP) |
| --intervalo | 30 | Segundos entre re-envíos |

## Requisitos
```bash
pip install scapy
sudo python3 dtp_vlan_hopping.py [opciones]
```

## Contra-medidas
| Medida | Comando Cisco |
|---|---|
| Deshabilitar DTP | `switchport nonegotiate` |
| Modo access fijo | `switchport mode access` |
| Cambiar VLAN nativa | `switchport trunk native vlan 999` |
| Limitar VLANs trunk | `switchport trunk allowed vlan 20,30` |

---
*Laboratorio académico | ITLA | Matrícula: 2023-0316*
