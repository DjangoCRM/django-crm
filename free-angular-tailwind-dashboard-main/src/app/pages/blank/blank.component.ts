import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { PageBreadcrumbComponent } from '../../shared/components/common/page-breadcrumb/page-breadcrumb.component';

@Component({
  selector: 'app-blank',
  imports: [
    CommonModule,
    PageBreadcrumbComponent,
  ],
  templateUrl: './blank.component.html',
  styles: ``
})
export class BlankComponent {

}
