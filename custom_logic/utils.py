import importlib
import json
from .models import CustomChart
from django.core.serializers.json import DjangoJSONEncoder


def load_logic(import_path):
    return importlib.import_module(import_path)


def execute_chartjs_config(code: str, context: dict) -> dict:
    exec_namespace = dict(context)  # copy context so we don't mutate it
    exec(code, exec_namespace, exec_namespace)  # shared global/local namespace
    config = exec_namespace.get("config", {})
    return json.loads(json.dumps(config))



def get_rendered_charts(user, page_key, context_data):
    charts = []
    user_charts = CustomChart.objects.filter(user=user).filter(pages__contains=[page_key])
    for chart in user_charts:
        try:
            chart_config = execute_chartjs_config(chart.config_code, context_data)  # <-- fixed: define chart_config
            config_json = json.dumps(chart_config, cls=DjangoJSONEncoder) if isinstance(chart_config, dict) else "{}"
            charts.append({
                "name": chart.name,
                "config": config_json,
                "card_size": chart.card_size,
                "error": None,
            })
        except Exception as e:
            charts.append({
                "name": chart.name,
                "config": "{}",
                "card_size": chart.card_size,
                "error": str(e),
            })
    return charts
