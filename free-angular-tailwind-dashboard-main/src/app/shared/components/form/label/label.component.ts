import { CommonModule } from '@angular/common';
import { Component,Input } from '@angular/core';

@Component({
  selector: 'app-label',
  imports: [CommonModule],
  templateUrl: './label.component.html',
  styles: ``
})
export class LabelComponent {
  @Input() for?: string;
  @Input() className = '';
}
