from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # TODO
        dizionario = {distributore.nome: [0,0] for distributore in self._distributori}
        for distributore in self._distributori:
            listaPrezzi = PrezzoDAO.get_prezzi(distributore.id)
            if listaPrezzi is None: return None
            for prezzo in listaPrezzi:
                if prezzo.data.month == mese:
                    dizionario[distributore.nome][0] += prezzo.prezzo_litro
                    dizionario[distributore.nome][1] += 1
        return [(el[0], el[1][0] / el[1][1]) for el in dizionario.items()]

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        #return sequenza_nomi, round(self.__costo_ottimo, 2)
        print(sequenza_nomi, round(self.__costo_ottimo, 2))

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # TODO
        costo_passaggio = 5
        if giorno == 8:
            if costo_corrente < self.__costo_ottimo or self.__costo_ottimo < 0:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale
            return
        if ultimo_distributore is None:
            if prezzi_settimana[1][0] < prezzi_settimana[2][0]: ultimo_distributore = 1
            else: ultimo_distributore = 2
            costo_corrente = costo_corrente + prezzi_settimana[ultimo_distributore][0]*100 #+ costo_passaggio
            sequenza_parziale = sequenza_parziale + [ultimo_distributore]
            giorno += 1

        #Rimango con lo stesso distributore
        distributore = ultimo_distributore
        self.__ricorsione(sequenza_parziale + [distributore],giorno+1,distributore,costo_corrente + prezzi_settimana[distributore][giorno-1]*100,prezzi_settimana)
        #Cambio distributore
        if ultimo_distributore == 1: distributore = 2
        else: distributore = 1
        self.__ricorsione(sequenza_parziale + [distributore],giorno+1,distributore,costo_corrente + prezzi_settimana[distributore][giorno-1]*100 + costo_passaggio,prezzi_settimana)

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        # TODO
        result = {distributore.id: [] for distributore in self._distributori}
        for distributore in self._distributori:
            listaPrezzi = PrezzoDAO.get_prezzi(distributore.id)
            if listaPrezzi is None: return None
            for prezzo in listaPrezzi:
                if prezzo.data.month == mese and prezzo.data.day <= 7:
                    result[distributore.id].append(prezzo.prezzo_litro)
        return result