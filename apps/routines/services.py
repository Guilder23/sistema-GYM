import requests
from django.conf import settings
from .models import Exercise, ExerciseCategory

class WgerService:
    BASE_URL = "https://wger.de/api/v2/"
    
    def __init__(self):
        # Wger API no requiere token para lecturas básicas, pero se puede configurar si es necesario
        self.headers = {
            'Accept': 'application/json',
        }

    def sync_categories(self):
        """Sincroniza las categorías de ejercicios desde Wger"""
        url = f"{self.BASE_URL}exercisecategory/"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            synced_count = 0
            for item in results:
                category, created = ExerciseCategory.objects.update_or_create(
                    wger_id=item['id'],
                    defaults={
                        'name': item['name'],
                    }
                )
                if created:
                    synced_count += 1
            return synced_count
        return 0

    def sync_exercises(self, limit=100, language_id=4):
        """
        Sincroniza ejercicios desde Wger usando exerciseinfo para obtener todo en una sola petición.
        """
        url = f"{self.BASE_URL}exerciseinfo/?limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            synced_count = 0
            for item in results:
                # Datos básicos del ejercicio
                exercise_data = item.get('exercise', {})
                wger_id = exercise_data.get('id')
                
                # Buscar traducción al idioma
                translations = item.get('translations', [])
                # Prioridad: Idioma solicitado > Inglés (2) > Primero disponible
                trans = next((t for t in translations if t.get('language') == language_id), None)
                if not trans:
                    trans = next((t for t in translations if t.get('language') == 2), None)
                if not trans and translations:
                    trans = translations[0]
                
                if not trans or not wger_id:
                    continue

                name = trans.get('name')
                description = trans.get('description', '')
                
                # Categoría
                cat_data = item.get('category', {})
                cat_wger_id = cat_data.get('id')
                
                # Imagen
                images = item.get('images', [])
                wger_image_url = None
                if images:
                    main_img = next((img for img in images if img.get('is_main')), images[0])
                    wger_image_url = main_img.get('image')

                # Obtener/Crear categoría
                category, _ = ExerciseCategory.objects.get_or_create(
                    wger_id=cat_wger_id,
                    defaults={'name': cat_data.get('name', 'General')}
                )

                exercise, created = Exercise.objects.update_or_create(
                    wger_id=wger_id,
                    defaults={
                        'name': name,
                        'description': description,
                        'category': category,
                        'wger_image_url': wger_image_url,
                    }
                )
                if created:
                    synced_count += 1
            return synced_count
        return 0
