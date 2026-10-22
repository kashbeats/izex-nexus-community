FROM grafana/grafana:13.2.1
USER root
RUN grafana cli plugins install volkovlabs-echarts-panel 7.2.5 && grafana cli plugins install yesoreyeram-infinity-datasource 4.1.1
USER 472
