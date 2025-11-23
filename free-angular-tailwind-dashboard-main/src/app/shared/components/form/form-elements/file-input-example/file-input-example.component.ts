import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ComponentCardComponent } from '../../../common/component-card/component-card.component';
import { LabelComponent } from '../../label/label.component';
import { FileInputComponent } from '../../input/file-input.component';

@Component({
  selector: 'app-file-input-example',
  imports: [
    CommonModule,
    ComponentCardComponent,
    LabelComponent,
    FileInputComponent
  ],
  template: `
   <app-component-card title="File Input">
    <div>
      <app-label>Upload file</app-label>
      <app-file-input (change)="handleFileChange($event)" className="custom-class"></app-file-input>
    </div>
  </app-component-card>
  `,
})
export class FileInputExampleComponent {
  handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      console.log('Selected file:', file.name);
    }
  }
}