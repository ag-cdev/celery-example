from celery import Celery
from flask import Flask, render_template, jsonify
from celery.result import AsyncResult
from celery import Task

from time import sleep

def make_celery(app):
    celery = Celery(app.name)
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(Task):  # Change CeleryTask to Task
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__)
    app.config.update(CELERY_CONFIG={
        'broker_url': 'redis://redis',
        'result_backend': 'redis://redis'
    })

    celery = make_celery(app)

    @celery.task(bind=True)
    def count(self):
        for i in range(40):
            self.update_state(state='PROGRESS', meta={'current': i, 'total': 40})
            print("Hello World:", i)
            sleep(1)
        return 'DONE!' 

    @app.route('/start')
    def start():
        task = count.apply_async()
        return render_template('start.html', task_id=task.id)

    @app.route('/cancel/<task_id>')
    def cancel(task_id):
        celery.control.revoke(task_id, terminate=True)  # Use the celery instance to access control
        return 'Canceled!'
    
    @app.route('/check_task/<task_id>')
    def check_task(task_id):
        task = AsyncResult(task_id, app=celery)
        if task.state == 'PROGRESS':
            progress = task.info.get('current', 0)
            total = task.info.get('total', 40)
            return jsonify({'status': 'PROGRESS', 'progress': progress, 'total': total})
        elif task.state == 'SUCCESS':
            return jsonify({'status': 'SUCCESS'})
        elif task.state == 'FAILURE':
            return jsonify({'status': 'FAILURE'})
        else:
            return jsonify({'status': 'PENDING'})

    return app, celery
