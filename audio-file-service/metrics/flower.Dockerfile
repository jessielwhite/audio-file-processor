FROM mher/flower
EXPOSE 5555
CMD ["celery", "--broker=redis://redis-add-registry-url:6379/0", "flower"]