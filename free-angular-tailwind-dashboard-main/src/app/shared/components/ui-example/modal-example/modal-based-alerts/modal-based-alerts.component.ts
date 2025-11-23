import { Component } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { ModalComponent } from '../../../ui/modal/modal.component';

@Component({
  selector: 'app-modal-based-alerts',
  imports: [
    ComponentCardComponent,
    ModalComponent,
  ],
  templateUrl: './modal-based-alerts.component.html',
  styles: ``
})
export class ModalBasedAlertsComponent {

  successModal = false;
  errorModal = false;
  infoModal = false;
  warningModal = false;

  handleOpenModal(modal: 'success' | 'error' | 'info' | 'warning') {
    if(modal === 'success') this.successModal = true;
    if(modal === 'error') this.errorModal = true;
    if(modal === 'info') this.infoModal = true;
    if(modal === 'warning') this.warningModal = true;
  }
  handleCloseModal(modal: 'success' | 'error' | 'info' | 'warning') {
    if(modal === 'success') this.successModal = false;
    if(modal === 'error') this.errorModal = false;
    if(modal === 'info') this.infoModal = false;
    if(modal === 'warning') this.warningModal = false;
  }
}
