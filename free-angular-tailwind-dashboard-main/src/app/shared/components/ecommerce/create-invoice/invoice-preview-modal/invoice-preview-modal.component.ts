import { Component } from '@angular/core';
import { ButtonComponent } from '../../../ui/button/button.component';
import { ModalComponent } from '../../../ui/modal/modal.component';

@Component({
  selector: 'app-invoice-preview-modal',
  imports: [
    ButtonComponent,
    ModalComponent,
  ],
  templateUrl: './invoice-preview-modal.component.html',
  styles: ``
})
export class InvoicePreviewModalComponent {
  isOpen = false;

  openModal() {
    this.isOpen = true;
  }

  closeModal() {
    this.isOpen = false;
  }
}
