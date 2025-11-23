import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { LabelComponent } from '../../label/label.component';
import { InputFieldComponent } from '../../input/input-field.component';
import { SelectComponent } from '../../select/select.component';
import { DatePickerComponent } from '../../date-picker/date-picker.component';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { TimePickerComponent } from '../../time-picker/time-picker.component';

@Component({
  selector: 'app-default-inputs',
  imports: [
    CommonModule,
    ComponentCardComponent,
    LabelComponent,
    InputFieldComponent,
    SelectComponent,
    DatePickerComponent,
    TimePickerComponent,
  ],
  templateUrl: './default-inputs.component.html',
  styles: ``
})
export class DefaultInputsComponent {

  showPassword = false;
  options = [
    { value: 'marketing', label: 'Marketing' },
    { value: 'template', label: 'Template' },
    { value: 'development', label: 'Development' },
  ];
  selectedOption = '';
  dateValue: any;
  timeValue = '';
  cardNumber = '';

  handleSelectChange(value: string) {
    this.selectedOption = value;
    console.log('Selected value:', value);
  }

  handleDateChange(event: any) {
    this.dateValue = event;
    console.log('Date changed:', event);
  }

  handleTimeChange(event: any) {
    this.timeValue = event.target.value;
    console.log(this.timeValue);
  }

  onTimeSelected(time: string) {
    console.log('Picked time:', time); // e.g. "10:45"
  }
}
