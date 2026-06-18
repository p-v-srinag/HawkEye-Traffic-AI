from app.tasks.celery_app import celery_app


@celery_app.task
def process_image(image_path):

    return {
        "status": "completed",
        "image": image_path
    }