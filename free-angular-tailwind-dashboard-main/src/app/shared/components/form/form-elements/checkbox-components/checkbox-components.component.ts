import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { CheckboxComponent } from '../../input/checkbox.component';


@Component({
  selector: 'app-checkbox-components',
  imports: [CommonModule,ComponentCardComponent,CheckboxComponent],
  templateUrl: './checkbox-components.component.html',
  styles: ``
})
export class CheckboxComponentsComponent {

  isChecked = false;
  isCheckedTwo = true;
  isCheckedDisabled = false;
}
