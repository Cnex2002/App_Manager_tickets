from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from .models import Ticket, SolucionTicket

class TicketSolutionSearch:
    def __init__(self):
        # Carga el modelo especializado en similitud semántica
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.tickets_data = []
        self.embeddings = None
        self.neigh = None
        self.load_data_and_build_index()

    def load_data_and_build_index(self):
        self.tickets_data = []
        textos = []

        for ticket in Ticket.objects.all():
            solucion = SolucionTicket.objects.filter(ticket=ticket).first()
            if solucion and ticket.descripcion and solucion.comentario:
                if len(solucion.comentario.strip()) > 10 and ticket.descripcion.lower() != 'nan':
                    texto = f"Problema: {ticket.descripcion} Solución: {solucion.comentario}"
                    self.tickets_data.append((ticket.id, texto))
                    textos.append(texto)

        if textos:
            # Genera embeddings con modelo SentenceTransformer
            self.embeddings = self.model.encode(textos, convert_to_numpy=True, normalize_embeddings=True)
            n_neighbors = min(3, len(self.embeddings))
            self.neigh = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
            self.neigh.fit(self.embeddings)
        else:
            self.embeddings = None
            self.neigh = None

    def query(self, texto_usuario, top_k=3, umbral_similitud=0.25):
        if not self.neigh:
            return []

        top_k = min(top_k, len(self.tickets_data))
        query_vec = self.model.encode([texto_usuario], convert_to_numpy=True, normalize_embeddings=True)
        distances, indices = self.neigh.kneighbors(query_vec, n_neighbors=top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            similitud = 1 - dist  # porque NearestNeighbors usa distancia
            if similitud >= umbral_similitud:
                ticket_id, texto = self.tickets_data[idx]

                # Dividir texto en problema y solución
                if "Solución:" in texto:
                    problema, solucion = texto.split("Solución:", 1)
                    problema = problema.replace("Problema:", "").strip()
                    solucion = solucion.strip()
                else:
                    problema = texto
                    solucion = "No se encontró una solución específica."

                results.append({
                    'ticket_id': ticket_id,
                    'problema': problema,
                    'solucion': solucion,
                    'similitud': round(similitud, 3)
                })
        return results

