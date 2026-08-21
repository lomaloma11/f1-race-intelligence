import os
import fastf1


class FastF1Client:
    """
    Cliente responsável por encapsular a comunicação com a biblioteca FastF1
    e gerenciar o cache local.
    """

    def __init__(self, cache_dir: str = "data/raw/cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(self.cache_dir)

    def get_session(self, year: int, event: str, session_type: str = "R"):
        """
        Carrega os dados de uma sessão específica.
        session_type pode ser: 'FP1', 'FP2', 'FP3', 'Q' (Qualifying), 'R' (Race)
        """
        try:
            session = fastf1.get_session(year, event, session_type)
            session.load()
            return session
        except Exception:
            return None
