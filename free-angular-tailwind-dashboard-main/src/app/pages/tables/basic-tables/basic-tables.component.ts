import { Component } from '@angular/core';
import { ComponentCardComponent } from '../../../shared/components/common/component-card/component-card.component';
import { PageBreadcrumbComponent } from '../../../shared/components/common/page-breadcrumb/page-breadcrumb.component';
import { BasicTableOneComponent } from '../../../shared/components/tables/basic-tables/basic-table-one/basic-table-one.component';
import { BasicTableTwoComponent } from '../../../shared/components/tables/basic-tables/basic-table-two/basic-table-two.component';
import { BasicTableThreeComponent } from '../../../shared/components/tables/basic-tables/basic-table-three/basic-table-three.component';
import { BasicTableFourComponent } from '../../../shared/components/tables/basic-tables/basic-table-four/basic-table-four.component';
import { BasicTableFiveComponent } from '../../../shared/components/tables/basic-tables/basic-table-five/basic-table-five.component';

@Component({
  selector: 'app-basic-tables',
  imports: [
    ComponentCardComponent,
    PageBreadcrumbComponent,
    BasicTableOneComponent,
    BasicTableTwoComponent,
    BasicTableThreeComponent,
    BasicTableFourComponent,
    BasicTableFiveComponent,
  ],
  templateUrl: './basic-tables.component.html',
  styles: ``
})
export class BasicTablesComponent {

}
