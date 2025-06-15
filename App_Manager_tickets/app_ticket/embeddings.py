from sentence_transformers import SentenceTransformer  # Modelo para generar vectores semánticos
from sklearn.neighbors import NearestNeighbors         # Algoritmo de búsqueda de vecinos más cercanos
from .models import Ticket, SolucionTicket             # Modelos de la base de datos

class TicketSolutionSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')  # Carga modelo de embeddings
        self.tickets_data = []      # Lista con ticket_id, problema y solución
        self.embeddings = None      # Vectores de texto para búsqueda
        self.neigh = None           # Índice de similitud (vecinos más cercanos)
        self.load_data_and_build_index()

    def load_data_and_build_index(self):
        self.tickets_data = []
        textos = []

        for ticket in Ticket.objects.all():  # Recorre todos los tickets
            solucion = SolucionTicket.objects.filter(ticket=ticket).first()  # Obtiene solución

            if solucion and ticket.descripcion and solucion.comentario:
                descripcion = ticket.descripcion.strip().lower()
                comentario = solucion.comentario.strip()

                if len(comentario) > 10 and descripcion != 'nan':  # Filtra entradas vacías o inválidas
                    self.tickets_data.append({
                        'ticket_id': ticket.id,
                        'problema': descripcion,
                        'solucion': comentario
                    })
                    textos.append(descripcion)  # Solo se vectoriza el problema

        if textos:
            # Genera vectores para los textos y crea el índice de similitud
            self.embeddings = self.model.encode(textos, convert_to_numpy=True, normalize_embeddings=True)
            n_neighbors = min(3, len(self.embeddings))  # Top K limitado
            self.neigh = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')  # Busca similitud coseno
            self.neigh.fit(self.embeddings)
        else:
            # No hay datos
            self.embeddings = None
            self.neigh = None

    def query(self, texto_usuario, top_k=3, umbral_similitud=0.35):
        if not self.neigh:
            return []

        texto_usuario = texto_usuario.strip().lower()
        query_vec = self.model.encode([texto_usuario], convert_to_numpy=True, normalize_embeddings=True)
        distances, indices = self.neigh.kneighbors(query_vec, n_neighbors=top_k)  # Busca vecinos más cercanos

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            similitud = 1 - dist  # Se transforma la distancia en similitud
            if similitud >= umbral_similitud:
                entry = self.tickets_data[idx]
                results.append({
                    'ticket_id': entry['ticket_id'],
                    'problema': entry['problema'],
                    'solucion': entry['solucion'],
                    'similitud': round(similitud, 3)
                })

        if not results:
            # Si ninguna coincidencia es suficientemente parecida
            results.append({
                'ticket_id': None,
                'problema': texto_usuario,
                'solucion': 'No se encontró una solución similar en los tickets previos.',
                'similitud': 0.0
            })

        return results
