import { Component } from '@angular/core';
import { PageBreadcrumbComponent } from '../../shared/components/common/page-breadcrumb/page-breadcrumb.component';
import { InvoiceSidebarComponent } from '../../shared/components/invoice/invoice-sidebar/invoice-sidebar.component';
import { InvoiceMainComponent } from '../../shared/components/invoice/invoice-main/invoice-main.component';

@Component({
  selector: 'app-invoices',
  imports: [
    PageBreadcrumbComponent,
    InvoiceSidebarComponent,
    InvoiceMainComponent
  ],
  templateUrl: './invoices.component.html',
  styles: ``
})
export class InvoicesComponent {

}
