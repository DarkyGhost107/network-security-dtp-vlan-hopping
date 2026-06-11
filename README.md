# DTP VLAN Hopping Tool - Matricula: 2023-0316 | ITLA

## Objetivo del Laboratorio
Demostrar dos tecnicas de VLAN Hopping:
1. **DTP Spoofing**: Enviar tramas DTP falsas para forzar al switch a negociar trunk.
2. **Doble Encapsulacion 802.1Q**: Enviar frames con dos etiquetas VLAN para saltar a VLANs restringidas.

> Solo para uso educativo en entornos de laboratorio controlados.

## Requisitos
- Linux (Kali Linux recomendado)
- Python 3.8+
- pip install scapy
- Privilegios root/sudo
- Interfaz conectada a puerto dynamic auto/desirable

## Uso
```bash
# Negociacion DTP (convertir puerto en trunk)
sudo python3 dtp_vlan_hopping.py -i eth0 -m dtp

# DTP + mantener trunk activo
sudo python3 dtp_vlan_hopping.py -i eth0 -m dtp -p

# VLAN Hopping con doble encapsulacion
sudo python3 dtp_vlan_hopping.py -i eth0 -m hopping --vlan-nativa 1 --vlan-objetivo 200 --ip-destino 20.23.3.100

# Ataque completo
sudo python3 dtp_vlan_hopping.py -i eth0 -m ambos --vlan-nativa 1 --vlan-objetivo 200 -p
```

## Parametros

| Parametro | Descripcion | Default |
|---|---|---|
| -i / --interfaz | Interfaz de red | eth0 |
| -m / --modo | dtp, hopping, ambos | requerido |
| --vlan-nativa | VLAN nativa del trunk | 1 |
| --vlan-objetivo | VLAN a atacar | 200 |
| --ip-destino | IP victima en VLAN objetivo | 20.23.3.100 |
| -p / --persistente | Mantener trunk con re-envio | False |

## Topologia (Matricula: 2023-0316)
```
Red Base: 20.23.3.0/24

ATACANTE (20.23.3.16 / Kali Linux)
   |
   | eth0 [dynamic auto -> TRUNK despues del ataque]
   |
SW-CORE (20.23.3.1)
   |-- Fa0/2 [access VLAN 10] -- Admin
   |-- Fa0/3 [access VLAN 30] -- Servidores
   |-- Fa0/24 [trunk] -- SW-ACC

PC-VICTIMA (20.23.3.100 / VLAN 200) <- objetivo del hopping

VLANs:
  VLAN 10  -> 20.23.3.0/28   Administracion
  VLAN 20  -> 20.23.3.16/28  Usuarios (atacante)
  VLAN 30  -> 20.23.3.32/28  Servidores
  VLAN 200 -> 20.23.3.96/28  Objetivo del hopping
```

## Funcionamiento del Script

### Estructura DTP
```
Ethernet 802.3 (dst: 01:00:0C:CC:CC:CC)
  LLC/SNAP (aa aa 03 00 00 0c 20 04)
    TLV 0x0001: Version = 0x01
    TLV 0x0002: Domain Name (32 bytes vacios)
    TLV 0x0003: Status = 0x8142 (Trunk/Desirable)
    TLV 0x0004: DTP Type = 0x8142 (Desirable)
    TLV 0x0005: Neighbor ID (MAC del atacante)
```

### Flujo del Ataque DTP
```
Atacante (Desirable)    Switch (dynamic auto)
      |--- DTP Desirable --->|
      |                      | Acepta negociacion
      |<-- DTP Desirable ----|
      |                      |
      |    [Trunk negociado]  |
      |<== VLAN 10 ==========|
      |<== VLAN 20 ==========| <- Atacante recibe todo
      |<== VLAN 200 =========|
```

### Flujo Doble Encapsulacion
```
Atacante    SW-Externo      SW-Interno    Victima
  |--[VLAN1][VLAN200]-->|               (VLAN 200)
                         | Elimina VLAN1
                         |--[VLAN200]-->|
                                        |--frame-->|
```

## Configuracion Cisco Vulnerable (solo para lab)
```
interface FastEthernet0/1
 switchport mode dynamic auto
```

## Contramediadas

### 1. Deshabilitar DTP (mas importante)
```
interface FastEthernet0/1
 switchport mode access
 switchport nonegotiate
```

### 2. Cambiar VLAN Nativa (contra doble encapsulacion)
```
interface FastEthernet0/24
 switchport trunk native vlan 999
vlan 999
 name VLAN-NATIVA-UNUSED
```

### 3. Limitar VLANs permitidas en trunk
```
interface FastEthernet0/24
 switchport trunk allowed vlan 10,20,30
```

### 4. Puertos no utilizados
```
interface range FastEthernet0/10-24
 shutdown
 switchport mode access
 switchport access vlan 999
```

| Contramediada | Protege contra | Efectividad |
|---|---|---|
| switchport nonegotiate | DTP Spoofing | Alta |
| switchport mode access | DTP Spoofing | Alta |
| Cambiar VLAN nativa | Doble encapsulacion | Alta |
| VLANs permitidas en trunk | Doble encapsulacion | Media |

---
*Laboratorio academico | ITLA | Matricula: 2023-0316*
