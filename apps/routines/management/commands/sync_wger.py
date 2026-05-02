from django.core.management.base import BaseCommand
from apps.routines.services import WgerService

class Command(BaseCommand):
    help = 'Sincroniza categorías y ejercicios desde la API de Wger'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Número máximo de ejercicios a sincronizar',
        )
        parser.add_argument(
            '--language',
            type=int,
            default=4,
            help='ID del idioma (4=Español, 2=Inglés)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        language = options['language']
        service = WgerService()

        self.stdout.write(self.style.SUCCESS('Iniciando sincronización con Wger API...'))

        # 1. Sincronizar anatomía (Músculos y Equipo)
        self.stdout.write('Sincronizando anatomía (Músculos y Equipo)...')
        service.sync_anatomy()

        # 2. Sincronizar ejercicios
        self.stdout.write(f'Sincronizando hasta {limit} ejercicios (Idioma ID: {language})...')
        exercises_count = service.sync_exercises(limit=limit, language_id=language)
        self.stdout.write(self.style.SUCCESS(f'Se sincronizaron {exercises_count} nuevos ejercicios.'))

        self.stdout.write(self.style.SUCCESS('Sincronización finalizada correctamente.'))
