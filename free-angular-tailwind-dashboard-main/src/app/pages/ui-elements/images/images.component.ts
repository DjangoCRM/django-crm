import { Component } from '@angular/core';
import { PageBreadcrumbComponent } from './../../../shared/components/common/page-breadcrumb/page-breadcrumb.component';
import { ComponentCardComponent } from '../../../shared/components/common/component-card/component-card.component';
import { ResponsiveImageComponent } from '../../../shared/components/ui/images/responsive-image/responsive-image.component';
import { ThreeColumnImageGridComponent } from '../../../shared/components/ui/images/three-column-image-grid/three-column-image-grid.component';
import { TwoColumnImageGridComponent } from '../../../shared/components/ui/images/two-column-image-grid/two-column-image-grid.component';

@Component({
  selector: 'app-images',
  imports: [
    PageBreadcrumbComponent,
    ComponentCardComponent,
    ResponsiveImageComponent,
    ThreeColumnImageGridComponent,
    TwoColumnImageGridComponent,
  ],
  templateUrl: './images.component.html',
  styles: ``
})
export class ImagesComponent {

}
