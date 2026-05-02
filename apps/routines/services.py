import requests
from django.conf import settings
from .models import Exercise, ExerciseCategory, Muscle, Equipment

class WgerService:
    BASE_URL = "https://wger.de/api/v2/"
    
    def __init__(self):
        self.headers = {'Accept': 'application/json'}

    def sync_anatomy(self):
        """Sincroniza músculos y equipamiento"""
        # Sincronizar Músculos
        response = requests.get(f"{self.BASE_URL}muscle/", headers=self.headers)
        if response.status_code == 200:
            for item in response.json().get('results', []):
                Muscle.objects.update_or_create(
                    wger_id=item['id'],
                    defaults={
                        'name': item['name'],
                        'is_front': item.get('is_front', True),
                        'image_url_main': item.get('image_url_main')
                    }
                )
        
        # Sincronizar Equipamiento
        response = requests.get(f"{self.BASE_URL}equipment/", headers=self.headers)
        if response.status_code == 200:
            for item in response.json().get('results', []):
                Equipment.objects.update_or_create(
                    wger_id=item['id'],
                    defaults={'name': item['name']}
                )

    def sync_exercises(self, limit=100, language_id=4):
        """
        Sincroniza ejercicios desde Wger usando exerciseinfo.
        """
        url = f"{self.BASE_URL}exerciseinfo/?limit={limit}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            synced_count = 0
            for item in results:
                wger_id = item.get('id')
                
                # Intentar obtener nombre en español (4) o inglés (2)
                translations = item.get('translations', [])
                trans = next((t for t in translations if t.get('language') == language_id), None)
                if not trans: trans = next((t for t in translations if t.get('language') == 2), None)
                
                if not trans or not wger_id:
                    continue

                name = trans.get('name')
                description = trans.get('description', '')

                category_data = item.get('category', {})
                category, _ = ExerciseCategory.objects.get_or_create(
                    wger_id=category_data.get('id'),
                    defaults={'name': category_data.get('name', 'General')}
                )

                # Imágenes
                images = item.get('images', [])
                wger_image_url = None
                if images:
                    main_img = next((img for img in images if img.get('is_main')), images[0])
                    wger_image_url = main_img.get('image')

                exercise, created = Exercise.objects.update_or_create(
                    wger_id=wger_id,
                    defaults={
                        'name': name,
                        'description': description,
                        'category': category,
                        'wger_image_url': wger_image_url,
                    }
                )
                
                # Músculos
                m_ids = [m['id'] for m in item.get('muscles', [])]
                m_ids += [m['id'] for m in item.get('muscles_secondary', [])]
                if m_ids:
                    muscle_objs = Muscle.objects.filter(wger_id__in=m_ids)
                    exercise.muscles.set(muscle_objs)
                
                # Equipo
                e_ids = [e['id'] for e in item.get('equipment', [])]
                if e_ids:
                    exercise.equipment.set(Equipment.objects.filter(wger_id__in=e_ids))

                if created: synced_count += 1
            return synced_count
        return 0
