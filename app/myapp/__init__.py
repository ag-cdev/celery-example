from celery import Celery
from celery.contrib.abortable import AbortableTask
from flask import Flask, render_template, jsonify
from celery.result import AsyncResult
from time import sleep

def make_celery(app):
    celery = Celery(app.name)
    celery.conf.update(app.config["CELERY_CONFIG"])
    return celery

class TestException(Exception):
    pass

def raise_exception(sleep_interval):
    sleep(sleep_interval)
    raise TestException('this function raises an exception')

def create_app():
    app = Flask(__name__)
    app.config.update(CELERY_CONFIG={
        'broker_url': 'redis://redis',
        'result_backend': 'redis://redis'
    })

    celery = make_celery(app)

    @celery.task(bind=True, base=AbortableTask)
    def count(self):
        for i in range(10):
            if i !=8:
                print("Hello World", i)
                self.update_state(state='PROGRESS', meta={'current': i, 'total': 10})
                sleep(1)
            else:
                try:
                    raise_exception(2)
                except TestException as exc:
                    self.update_state(state='FAILURE', meta={'exc_type':type(exc).__name__})
                    print('Caught exception: {}'.format(exc))
                    raise                
        return 'DONE!' 

    @app.route('/start')
    def start():
        task = count.delay()
        return render_template('start.html', task=task)


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