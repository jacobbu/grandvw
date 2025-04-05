from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from video.models import Video, Detection
import plotly.express as px
import plotly.io as pio
from django.db import models
from .forms import DataForm


@login_required
def Add_Figure(request):
    user = request.user
    videos = Video.objects.filter(created_by=user)
    detection_logs = Detection.objects.filter(camera__in=videos)

    graph1 = graph2 = graph3 = None  # default to empty

    if detection_logs.exists():
        # 1. Scatter Plot
        fig1 = px.scatter(
            detection_logs.values('timestamp', 'label'),
            x='timestamp',
            y='label',
            title='Objects Detected Over Time',
            labels={'label': 'Detected Object'}
        )
        graph1 = pio.to_html(fig1, full_html=False)

        # Aggregate once
        object_counts = (
            detection_logs.values('label')
            .annotate(count=models.Count('label'))
            .order_by('-count')
        )

        # 2. Pie Chart
        fig2 = px.pie(
            object_counts,
            names='label',
            values='count',
            title='Object Detection Breakdown (Percentage)'
        )
        graph2 = pio.to_html(fig2, full_html=False)

        # 3. Bar Graph
        fig3 = px.bar(
            object_counts,
            x='label',
            y='count',
            title='Detections per Object Type',
            labels={'label': 'Object', 'count': 'Number of Detections'}
        )
        graph3 = pio.to_html(fig3, full_html=False)

    # Form logic (if needed)
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.created_by = request.user
            data.save()
            return redirect('/')
    else:
        form = DataForm()

    return render(request, 'data/add_figure.html', {
        'form': form,
        'graph1': graph1,
        'graph2': graph2,
        'graph3': graph3,
    })
