import os
import requests
import socket
import ipaddress

# ===============================
# UTILS
# ===============================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    print("""
======================================
           OSINT TOOL v2.0
======================================
    """)

# ===============================
# IP LOOKUP
# ===============================

def ip_lookup(ip: str) -> str:
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return "IP non valido."

    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return "Errore durante la richiesta all'API."

    return (
        "\n=== RISULTATI IP LOOKUP ===\n"
        f"IP: {data.get('ip', 'N/D')}\n"
        f"Città: {data.get('city', 'N/D')}\n"
        f"Regione: {data.get('region', 'N/D')}\n"
        f"Nazione: {data.get('country', 'N/D')}\n"
        f"Provider: {data.get('org', 'N/D')}\n"
        f"Coordinate: {data.get('loc', 'N/D')}\n"
    )

# ===============================
# DNS LOOKUP
# ===============================

def dns_lookup(domain: str) -> str:
    try:
        ip = socket.gethostbyname(domain)
        return (
            "\n=== DNS LOOKUP ===\n"
            f"Dominio: {domain}\n"
            f"IP associato: {ip}\n"
        )
    except Exception:
        return "Errore nel DNS lookup."

# ===============================
# USERNAME SCAN (placeholder)
# ===============================

def username_scan(username: str) -> str:
    return (
        "\n=== USERNAME SCAN ===\n"
        f"Username: {username}\n"
        "Modulo non attivo. Puoi collegare Sherlock qui.\n"
    )

# ===============================
# EMAIL SCAN (placeholder)
# ===============================

def email_scan(email: str) -> str:
    return (
        "\n=== EMAIL SCAN ===\n"
        f"Email: {email}\n"
        "Modulo non attivo. Puoi collegare Holehe qui.\n"
    )

# ===============================
# MENU PRINCIPALE
# ===============================

def menu():
    while True:
        clear()
        banner()

        print("1. Ricerca IP")
        print("2. DNS Lookup")
        print("3. Username Scan")
        print("4. Email Scan")
        print("5. Esci")

        scelta = input("\nSeleziona un'opzione: ")

        if scelta == "1":
            ip = input("Inserisci IP: ")
            print(ip_lookup(ip))
            input("\nPremi INVIO per continuare...")

        elif scelta == "2":
            dominio = input("Inserisci dominio: ")
            print(dns_lookup(dominio))
            input("\nPremi INVIO per continuare...")

        elif scelta == "3":
            username = input("Inserisci username: ")
            print(username_scan(username))
            input("\nPremi INVIO per continuare...")

        elif scelta == "4":
            email = input("Inserisci email: ")
            print(email_scan(email))
            input("\nPremi INVIO per continuare...")

        elif scelta == "5":
            print("\nUscita dal programma...")
            break

        else:
            print("Scelta non valida.")
            input("Premi INVIO per continuare...")

# ===============================
# AVVIO PROGRAMMA
# ===============================

if __name__ == "__main__":
    menu()
