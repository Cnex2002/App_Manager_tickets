from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.neighbors import NearestNeighbors

from .models import Ticket, SolucionTicket

class TicketSolutionSearch:
    def __init__(self):
        # Carga modelo de embeddings (puedes cambiar el modelo por uno más pequeño si quieres)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.tickets_data = []
        self.embeddings = None
        self.neigh = None
        self.load_data_and_build_index()

    def load_data_and_build_index(self):
        # Obtén todos los tickets que tengan solución
        self.tickets_data = []
        textos = []

        for ticket in Ticket.objects.all():
            # Buscar solución relacionada (puede haber más de una, aquí tomamos la primera)
            solucion = SolucionTicket.objects.filter(ticket=ticket).first()
            if solucion:
                # Unimos texto problema + solución
                texto = f"Problema: {ticket.descripcion} Solución: {solucion.comentario}"
                self.tickets_data.append((ticket.id, texto))
                textos.append(texto)

        if textos:
            # Genera embeddings para todos los textos
            self.embeddings = self.model.encode(textos)
            # Número de vecinos máximo = cantidad de datos o 3, lo que sea menor
            n_neighbors = min(3, len(self.embeddings))
            self.neigh = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
            self.neigh.fit(self.embeddings)
        else:
            self.embeddings = None
            self.neigh = None


    def query(self, texto_usuario, top_k=3):
        if not self.neigh:
            return []

        # Limitar top_k al máximo número de datos que tenemos
        top_k = min(top_k, len(self.tickets_data))

        query_vec = self.model.encode([texto_usuario])
        distances, indices = self.neigh.kneighbors(query_vec, n_neighbors=top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            ticket_id, texto = self.tickets_data[idx]
            results.append({'ticket_id': ticket_id, 'texto': texto, 'distancia': dist})
        return results

