import { Component, NgZone, ElementRef, ViewChild } from '@angular/core';
import * as am5 from "@amcharts/amcharts5";
import * as am5map from "@amcharts/amcharts5/map";
import am5geodata_worldLow from "@amcharts/amcharts5-geodata/worldLow";

@Component({
  selector: 'app-country-map',
  template: `<div #chartdiv style="width: 100%; height: 300px; border-radius: 1rem;"></div>`,
})
export class CountryMapComponent {
  @ViewChild('chartdiv', { static: true }) chartdiv!: ElementRef;
  root!: am5.Root;

  constructor(private zone: NgZone) { }

  ngOnInit() {
    this.zone.runOutsideAngular(() => {
      this.root = am5.Root.new(this.chartdiv.nativeElement);

      let chart = this.root.container.children.push(
        am5map.MapChart.new(this.root, {
          panX: "none",
          panY: "none",
          wheelX: "none",
          wheelY: "none",
          projection: am5map.geoMercator(),
        })
      );

      let polygonSeries = chart.series.push(
        am5map.MapPolygonSeries.new(this.root, {
          geoJSON: am5geodata_worldLow,
          exclude: ["AQ"],
        })
      );

      polygonSeries.mapPolygons.template.setAll({
        tooltipText: "{name}",
        interactive: true,
        fill: am5.color(0xE5EAF2),
        stroke: am5.color(0xD0D5DD),
      });

      polygonSeries.mapPolygons.template.states.create("hover", {
        fill: am5.color(0x465FFF),
      });

      // Add blue dot markers
      let pointSeries = chart.series.push(
        am5map.MapPointSeries.new(this.root, {})
      );

      const markers = [
        { lat: 37.2580397, lon: -104.657039, name: "United States" },
        { lat: 20.7504374, lon: 73.7276105, name: "India" },
        { lat: 53.613, lon: -11.6368, name: "United Kingdom" },
        { lat: -25.0304388, lon: 115.2092761, name: "Sweden" },
      ];

      markers.forEach(m => {
        let point = pointSeries.pushDataItem({
          latitude: m.lat,
          longitude: m.lon,
        });

        let circle = am5.Circle.new(this.root, {
          radius: 6,
          fill: am5.color(0x465FFF),
          stroke: am5.color(0xffffff),
          strokeWidth: 2,
        });
        circle.set("tooltipText", m.name);

        pointSeries.bullets.push(() =>
          am5.Bullet.new(this.root, {
            sprite: am5.Circle.new(this.root, {
              radius: 6,
              fill: am5.color(0x465FFF),
              stroke: am5.color(0xffffff),
              strokeWidth: 2,
              tooltipText: m.name
            })
          })
        );
      });
    });
  }

  ngOnDestroy() {
    this.root?.dispose();
  }
}