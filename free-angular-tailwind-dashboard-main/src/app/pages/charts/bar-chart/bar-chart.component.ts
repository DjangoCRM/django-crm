import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { BarChartOneComponent } from '../../../shared/components/charts/bar/bar-chart-one/bar-chart-one.component';
import { PageBreadcrumbComponent } from '../../../shared/components/common/page-breadcrumb/page-breadcrumb.component';
import { ComponentCardComponent } from '../../../shared/components/common/component-card/component-card.component';

@Component({
  selector: 'app-bar-chart',
  imports: [
    CommonModule,
    ComponentCardComponent,
    PageBreadcrumbComponent,
    BarChartOneComponent,
  ],
  templateUrl: './bar-chart.component.html',
  styles: ``
})
export class BarChartComponent {

}
