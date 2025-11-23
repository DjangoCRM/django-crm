import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { InvoiceTableComponent } from '../invoice-table/invoice-table.component';
import { ButtonComponent } from '../../ui/button/button.component';

@Component({
  selector: 'app-invoice-main',
  imports: [
    CommonModule,
    InvoiceTableComponent,
    ButtonComponent
],
  templateUrl: './invoice-main.component.html',
  styles: ``
})
export class InvoiceMainComponent {

}
