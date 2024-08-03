import requests
import json
import inspect
import sys

from colorama import Fore, Style
if sys.version_info < (3, 8):
    exit("Python 3.8 lub wyższy jest wymagany do uruchomienia tego bota! >:C")
try:
    from discord import app_commands, Intents, Client, Interaction
except ImportError:
    exit(
        "Albo discord.py nie jest zainstalowany, albo uruchamiasz jego starszą i nieobsługiwaną wersję."
        "Sprawdź, czy masz najnowszą wersję discord.py! (spróbuj przeinstalować wymagania?)"
    )

logo = f"""
Aktualnie starasz się o discord active developer badge!
"""
print(logo + inspect.cleandoc(f"""
    Hej, Witam w programie, który umożliwia zdobycie aktywnej odznaki dewelopera discord!
    Wpisz poniżej token swojego bota, aby kontynuować.

    {Style.DIM}Nie zamykaj tej aplikacji po wprowadzeniu tokena
    Możesz ją zamknąć po zaproszeniu bota i uruchomieniu polecenia{Style.RESET_ALL}
"""))

try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}


while True:
    token = config.get("token", None)
    if token:
        print(f"\n--- Wykryto token w {Fore.GREEN}./config.json{Fore.RESET} (zapisany z poprzedniego uruchomienia). Użycie zapisanego tokena. ---\n")
    else:
        token = input("> ")
    try:
        data = requests.get("https://discord.com/api/v10/users/@me", headers={
            "Authorization": f"Bot {token}"
        }).json()
    except requests.exceptions.RequestException as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            exit(f"{Fore.RED}ConnectionError{Fore.RESET}: Discord jest powszechnie blokowany w sieciach publicznych, upewnij się, że discord.com jest osiągalny!")

        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"{Fore.RED}Timeout{Fore.RESET}: Połączenie z API Discorda wygasło (możliwe, że jest ograniczone?).")
        exit(f"Wystąpił nieznany błąd! Dodatkowe informacje:\n{e}")
    if data.get("id", None):
        break
    print(f"\nSeems like you entered an {Fore.RED}invalid token{Fore.RESET}. Please enter a valid token (see Github repo for help).")
    config.clear()
with open("config.json", "w") as f:
    config["token"] = token
    json.dump(config, f, indent=2)


class FunnyBadge(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ Jest on wywoływany podczas uruchamiania bota, aby skonfigurować globalne polecenia """
        await self.tree.sync()

client = FunnyBadge(intents=Intents.none())


@client.event
async def on_ready():
    """ Jest to wywoływane, gdy bot jest gotowy i ma połączenie z Discordem.
        Wypisuje również adres URL zaproszenia bota, który automatycznie używa Twojego
        Client ID, aby upewnić się, że zapraszasz właściwego bota z właściwymi zakresami.
    """
    print(inspect.cleandoc(f"""
        Zalogowano jako {client.user} (ID: {client.user.id})

        Uzyj tego adresu, aby zaprosić bota {client.user} na swój serwer:
        {Fore.LIGHTBLUE_EX}https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot{Fore.RESET}
    """), end="\n\n")


@client.tree.command()
async def odznaka(interaction: Interaction):
    """ Przywitanie czy coś. """
    print(f"> {Style.BRIGHT}{interaction.user}{Style.RESET_ALL} użył komendy /odznaka.")

    await interaction.response.send_message(inspect.cleandoc(f"""
        No siema **{interaction.user}!**

        > __**Pewnie zastanawiasz się, twoja moja odznaka?**__
        > Odznaka zostanie nadana tobie do 24h, od momentu wpisania
        > tej komendy, musi minąć minimum 24h, ja np. czekałem 3dni, ale no
        > w tej chwili 24 godziny to zalecany czas oczekiwania przed kolejną próbą wpisania komendy.

        > __**Minęły 24 godziny, nadal nie mam odznaki.**__
        > Jeśli minęły już 24 godziny, możesz udać się do
        > https://discord.com/developers/active-developer i wypełnić tam "formularz".
        > Jeśli nadal ci się nie pokazał to ponów komendę. (Najlepiej jak znajomy ją też wpiszę)

        > __**Aktualizacje odznaki Aktywnego Dewelopera**__
        > Aktualizacje dotyczące odznaki Active Developer można znaleźć na
        > Serwerze Discord dla deweloperów https://discord.gg/discord-developers na kanale #active-dev-badge
    """))

client.run(token)
