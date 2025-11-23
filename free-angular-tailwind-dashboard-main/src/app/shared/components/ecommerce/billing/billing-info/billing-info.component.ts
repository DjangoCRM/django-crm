import { Component } from '@angular/core';
import { ModalComponent } from '../../../ui/modal/modal.component';
import { ButtonComponent } from '../../../ui/button/button.component';

@Component({
  selector: 'app-billing-info',
  imports: [
    ModalComponent,
    ButtonComponent,
  ],
  templateUrl: './billing-info.component.html',
  host: {
    class: 'rounded-2xl border border-gray-200 bg-white xl:w-2/6 dark:border-gray-800 dark:bg-white/[0.03]',
  },
})
export class BillingInfoComponent {

  isOpen = false;

  openModal() {
    this.isOpen = true;
  }

  closeModal() {
    this.isOpen = false;
  }

  handleSave ()  {
    // Handle save logic here
    console.log("Saving changes...");
    this.closeModal();
  };
}
