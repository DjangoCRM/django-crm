import { Component } from '@angular/core';
import { TextAreaComponent } from '../../input/text-area.component';
import { CommonModule } from '@angular/common';
import { LabelComponent } from '../../label/label.component';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';

@Component({
  selector: 'app-text-area-input',
  imports: [
    TextAreaComponent,
    CommonModule,
    LabelComponent,
    ComponentCardComponent,
  ],
  templateUrl: './text-area-input.component.html',
  styles: ``
})
export class TextAreaInputComponent {

  message = '';
  messageTwo = '';
}
