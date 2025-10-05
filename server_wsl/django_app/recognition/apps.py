from django.apps import AppConfig


class RecognitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recognition'

    def ready(self):
        print("Recognition app ready")
        import os
        if os.environ.get('RUN_MAIN') == 'true':  #这里必须得是小写字符串'true'
            from .recognition import load_known_faces
            load_known_faces()
            print("Successfully run load_known_faces")

            from recognition.scheduler import start
            start()