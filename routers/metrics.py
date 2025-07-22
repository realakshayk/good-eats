from fastapi import APIRouter, Response
from utils.logger import get_prometheus_metrics

router = APIRouter(prefix="/metrics", tags=["Monitoring"])

@router.get("/", response_class=Response, include_in_schema=False)
def prometheus_metrics():
    metrics = get_prometheus_metrics()
    return Response(content=metrics, media_type="text/plain") 