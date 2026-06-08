from trello import TrelloClient
from datetime import datetime, timezone

class Trello:
    # Enums para combinar com as chamadas do seu ContextBuilder
    class status:
        BLOCKED = "blocked"
        OVERDUE = "overdue"

    def __init__(self, config_data):
        """
        config_data deve ser um dicionário contendo:
        {
            "key": "sua_trello_key",
            "token": "seu_trello_token",
            "board_id": "id_do_quadro_da_ouvai"
        }
        """
        self.client = TrelloClient(
            api_key=config_data.get("key"),
            api_secret=config_data.get("token") # A lib chama o Token de api_secret
        )
        self.board = self.client.get_board(config_data.get("board_id"))

    def get_cards(self, status):
        """Busca cartões do quadro filtrando por regras de negócio (Impedidos ou Atrasados)."""
        all_cards = self.board.all_cards()
        filtered_cards = []

        if status == Trello.status.BLOCKED:
            # Estratégia: Procura cartões que estão em uma coluna chamada "Impedido", "Travado" 
            # ou que contenham uma etiqueta/label escrita "Impedido"
            for card in all_cards:
                list_name = card.get_list().name.lower()
                labels = [label.name.lower() for label in card.labels]
                
                if "impedido" in list_name or "travado" in list_name or "impedido" in labels:
                    # Trazemos o nome do card e quem está nele para o gerente saber cobrar
                    members = [m.username for m in card.get_members()]
                    filtered_cards.append(f"{card.name} (Responsável: {', '.join(members) if members else 'Sem dono'})")

        elif status == Trello.status.OVERDUE:
            # Estratégia: Verifica se o card tem data de entrega (due) e se ela já passou
            now = datetime.now(timezone.utc)
            for card in all_cards:
                if card.due_date:
                    # Se a data de entrega passou e o card não está marcado como concluído
                    if card.due_date < now and not card.is_due_complete:
                        members = [m.username for m in card.get_members()]
                        filtered_cards.append(f"{card.name} (Atrasado desde: {card.due_date.strftime('%d/%m')})")

        return filtered_cards